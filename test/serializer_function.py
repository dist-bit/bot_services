from enum import Enum
import inspect
from typing import List, Optional, get_type_hints
import unittest
from loguru import logger

def get_type_name(typ):
    if hasattr(typ, '__origin__'):
        origin = typ.__origin__.__name__.lower()
        if origin == "list":
            return "array"
        return origin
    return getattr(typ, '__name__', str(typ)).lower()

def parse_docstring(docstring):
    if not docstring:
        return "", {}
    
    lines = inspect.cleandoc(docstring).split('\n')
    description = []
    params = {}
    
    mode = "description"
    current_param = ""
    
    for line in lines:
        line = line.strip()
        if line.lower() in ["args:", "parameters:"]:
            mode = "params"
        elif mode == "description":
            description.append(line)
        elif mode == "params":
            if ':' in line:
                current_param, param_desc = line.split(':', 1)
                current_param = current_param.strip()
                params[current_param] = param_desc.strip()
            elif current_param and line:
                params[current_param] += " " + line
    
    return "\n".join(description).strip(), params

def serialize_function_to_json(func, required_params: Optional[List[str]] = None):
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    description, param_descriptions = parse_docstring(func.__doc__)
    
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
            "type": param_type,
            "description": param_descriptions.get(name, "")
        }
        
        if isinstance(param.annotation, type) and issubclass(param.annotation, Enum):
            param_info["type"] = "string"
            param_info["enum"] = [e.value for e in param.annotation]
        
        if param.default is not param.empty and not isinstance(param.default, Enum):
            param_info["default"] = param.default
        
        function_info["parameters"]["properties"][name] = param_info
    
    return function_info


class StructuredResponse:
    @staticmethod
    def success(message, response_with_llm=False, mark_as_complete=False, data=None):
        return {"message": message, "data": data}

class CurrencyConverter:
    def convert(self, amount, from_currency, to_currency):
        # Mock implementation for testing
        return amount * 20  # Assuming 1 USD = 20 MXN for simplicity

class TestFunctions:
    @staticmethod
    def convert_usd_to_mxn(amount: float) -> StructuredResponse:
        """
        Convert amount in usd to mexican pesos

        Args:
            amount: quantity in number to convert

        Returns:
            StructuredResponse: Response indicating success or failure of conversion.
        """
        c = CurrencyConverter()
        total = c.convert(amount, 'USD', 'MXN')
        return StructuredResponse.success("La conversión se realizó con éxito", response_with_llm=True, mark_as_complete=False, data={
            "cantidad a convertir en dólares": amount,
            "valor convertido en pesos": total
        })
    
    class TemperatureUnit(Enum):
        CELSIUS = "celsius"
        FAHRENHEIT = "fahrenheit"

    def get_weather(location: str, days: int, unit: TemperatureUnit = TemperatureUnit.CELSIUS) -> List[dict]:
        """
        Get weather forecast for a specific location.

        Args:
            location: The city and state, e.g. San Francisco, CA
            days: Number of days for the forecast
            unit: Temperature unit (celsius or fahrenheit)

        Returns:
            A list of dictionaries containing daily weather information
        """
        pass

class TestSerializeFunctionToJson(unittest.TestCase):
    def test_serialize_convert_usd_to_mxn(self):
        result = serialize_function_to_json(TestFunctions.convert_usd_to_mxn, required_params=["amount"])
        logger.debug(result)
        
        self.assertEqual(result["name"], "convert_usd_to_mxn")
        self.assertIn("Convert amount in usd to mexican pesos", result["description"])
        
        self.assertIn("parameters", result)
        self.assertIn("properties", result["parameters"])
        self.assertIn("amount", result["parameters"]["properties"])
        
        amount_param = result["parameters"]["properties"]["amount"]
        self.assertEqual(amount_param["type"], "float")
        
        self.assertIn("required", result["parameters"])
        self.assertIn("amount", result["parameters"]["required"])
        
        self.assertIn("returns", result)
        self.assertEqual(result["returns"]["type"], "structuredresponse")
        self.assertIn("Response indicating success or failure of conversion", result["returns"]["description"])

if __name__ == '__main__':
    unittest.main()