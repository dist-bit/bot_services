import inspect
import re
import xml.etree.ElementTree as ET
import json
import ast
from loguru import logger
from typing import List, get_type_hints, Optional

def get_type_name(typ):
    return getattr(typ, '__name__', str(typ))

def parse_docstring(docstring):
    if not docstring:
        return "", {}, ""
    
    lines = inspect.cleandoc(docstring).split('\n')
    description = []
    params = {}
    returns = ""
    
    mode = "description"
    current_param = ""
    
    for line in lines:
        if line.strip().lower() == "args:":
            mode = "params"
        elif line.strip().lower() == "returns:":
            mode = "returns"
        elif mode == "description":
            description.append(line)
        elif mode == "params":
            if ':' in line:
                current_param, param_desc = line.split(':', 1)
                current_param = current_param.strip()
                params[current_param] = param_desc.strip()
            elif current_param and line.strip():
                params[current_param] += " " + line.strip()
        elif mode == "returns" and line.strip():
            returns += line.strip() + " "
    
    return "\n".join(description).strip(), params, returns.strip()

def serialize_function_to_json(func, required_params: Optional[List[str]] = None):
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    description, param_descriptions, return_description = parse_docstring(func.__doc__)
    
    function_info = {
        "name": func.__name__,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": {},
        }
    }
    
    if required_params is not None:
        function_info["parameters"]["required"] = required_params
    
    for name, param in signature.parameters.items():
        param_type = get_type_name(type_hints.get(name, type(None)))
        param_info = {
            "type": param_type.lower(),
            "description": param_descriptions.get(name, "")
        }
        
        if param.default != inspect.Parameter.empty:
            param_info["default"] = param.default
        
        function_info["parameters"]["properties"][name] = param_info
    
    return_type = type_hints.get('return', type(None))
    if return_type is not type(None):
        function_info["returns"] = {
            "type": get_type_name(return_type).lower(),
            "description": return_description
        }
    
    return function_info #json.dumps(function_info, indent=2)

def validate_and_extract_tool_calls(assistant_content):
    validation_result = False
    tool_calls = []
    error_message = None

    try:
        # wrap content in root element
        xml_root_element = f"<root>{assistant_content}</root>"
        root = ET.fromstring(xml_root_element)

        # extract JSON data
        for element in root.findall(".//tool_call"):
            json_data = None
            try:
                json_text = element.text.strip()

                try:
                    # Prioritize json.loads for better error handling
                    json_data = json.loads(json_text)
                except json.JSONDecodeError as json_err:
                    try:
                        # Fallback to ast.literal_eval if json.loads fails
                        json_data = ast.literal_eval(json_text)
                    except (SyntaxError, ValueError) as eval_err:
                        error_message = f"JSON parsing failed with both json.loads and ast.literal_eval:\n"\
                                        f"- JSON Decode Error: {json_err}\n"\
                                        f"- Fallback Syntax/Value Error: {eval_err}\n"\
                                        f"- Problematic JSON text: {json_text}"
                        logger.error(error_message)
                        continue
            except Exception as e:
                error_message = f"Cannot strip text: {e}"
                logger.error(error_message)

            if json_data is not None:
                tool_calls.append(json_data)
                validation_result = True

    except ET.ParseError as err:
        error_message = f"XML Parse Error: {err}"
        logger.error(f"XML Parse Error: {err}")

    # Return default values if no valid data is extracted
    return validation_result, tool_calls, error_message


def extract_json_from_markdown(text):
    """
    Extracts the JSON string from the given text using a regular expression pattern.
    
    Args:
        text (str): The input text containing the JSON string.
        
    Returns:
        dict: The JSON data loaded from the extracted string, or None if the JSON string is not found.
    """
    json_pattern = r'```json\r?\n(.*?)\r?\n```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        json_string = match.group(1)
        try:
            data = json.loads(json_string)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON string: {e}")
    else:
        logger.warning("JSON string not found in the text.")
    return None