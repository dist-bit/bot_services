from typing import List
from implementations.abstract_functions_client import AbstractClientFunctions
from store.redis import Redis
from engine.engine import Engine
from engine.utils import validate_and_extract_tool_calls
from engine.validator import validate_function_call_schema
from loguru import logger


who_i_am = """You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags. You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug into functions. Transform quantities to numbers. Here are the available tools: 
<tools>
   %s
</tools>

Use the following pydantic model json schema for each tool call you will make: {'title': 'FunctionCall', 'type': 'object', 'properties': {'arguments': {'title': 'Arguments', 'type': 'object'}, 'name': {'title': 'Name', 'type': 'string'}}, 'required': ['arguments', 'name']} For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:
<tool_call>
{'arguments': <args-dict>, 'name': <function-name>}
</tool_call>


If the input is a question or dude from user, always call capture_user_question function.
"""


class ToolCaller:

    def __init__(self, client_functions: AbstractClientFunctions) -> None:
        self.client_functions = client_functions
        self.tools = client_functions.get_openai_tools()
        self.functions_to_apply = client_functions.serializer()
     
        self.engine = Engine()
        self.redis = Redis()

    def _execute_function_call(self, tool_call, report: str):    
        function_name = tool_call.get("name")
        if not any(func['name'] == function_name for func in self.functions_to_apply):
            raise ValueError(f"Function {function_name} is not in the list of functions to apply")
        function_to_call = getattr(self.client_functions, function_name, None)
        if function_to_call is None:
            raise AttributeError(f"Function {function_name} is not defined in client functions")
        function_args = tool_call.get("arguments", {})
        logger.info(f"Invoking function call {function_name} with args {function_args}")
        self.redis.store_value("report", report)

        function_args = tool_call.get("arguments", {})
        function_response = function_to_call(*function_args.values())
        
        self.redis.delete_value("report")
        return {"name": function_name, "content": function_response}

    def process_input_tool(self, msg: str, functions: List[str], report: str):
        filtered_functions = [f for f in self.functions_to_apply if f['name'] in functions]

        functions_str = "\n".join(str(f) for f in filtered_functions)
        who_i_am_updated = who_i_am % functions_str

        messages = [
            {
                "role": "system",
                "content": who_i_am_updated,
            },
            {
                "role": "user",
                "content": msg,
            }
        ]

        response = self.engine.call_llm(messages=messages)

        _, tool_calls, _ = validate_and_extract_tool_calls(response)

        responses = []
        for tool_call in tool_calls:
            validation, _ = validate_function_call_schema(
                tool_call, self.tools)

            if validation:
                function_response = self._execute_function_call(
                    tool_call, report)
                responses.append(function_response)

        return responses
