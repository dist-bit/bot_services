from typing import Any, Callable, Dict, List
from database.mongo import MongoDB
from engine.utils import serialize_function_to_json
from implementations.abstract_functions_client import AbstractClientFunctions
from langchain_core.utils.function_calling import convert_to_openai_tool
from implementations.response import StructuredResponse
from store.redis import Redis
from currency_converter import CurrencyConverter


class TestFunctions(AbstractClientFunctions):
    redis = Redis()
    db = None
    session = None

    def __init__(self, db: MongoDB, session):
        TestFunctions.db = db
        TestFunctions.session = session


    @staticmethod
    def convert_usd_to_mxn(amount: float) -> StructuredResponse:
        """
        Convert amount in usd to mexican pesos

        Returns:
            StructuredResponse: Response indicating success or failure of conversion.
        """
        c = CurrencyConverter()
        total = c.convert(amount, 'USD', 'MXN')
        return StructuredResponse.success("La conversión se realizó con éxito", response_with_llm=True, mark_as_complete=False, data={
            "cantidad a convertir en dólares": amount,
            "valor convertido en pesos": total
        })

    @staticmethod
    def convert_mxn_to_usd(amount: float) -> StructuredResponse:
        """
        Convert amount in mexican pesos to usd

        Returns:
            StructuredResponse: Response indicating success or failure of conversion.
        """
        c = CurrencyConverter()
        total = c.convert(amount, 'MXN', 'USD')
        return StructuredResponse.success("La conversión se realizó con éxito", response_with_llm=True, mark_as_complete=False, data={
            "cantidad a convertir en pesos": amount,
            "valor convertido en dólares": total
        })

    def get_media_tools(self) -> Dict[str, Callable]:
       return {}

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        llm_functions = [
            TestFunctions.convert_usd_to_mxn,
            TestFunctions.convert_mxn_to_usd
        ]

        return [convert_to_openai_tool(f) for f in llm_functions]
    

    def serializer(self):
        llm_functions = [
            serialize_function_to_json(TestFunctions.convert_usd_to_mxn, required_params=["amount"]),
            serialize_function_to_json(TestFunctions.convert_mxn_to_usd, required_params=["amount"])
        ]
        
        return llm_functions