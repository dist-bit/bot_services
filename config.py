import os
from typing import Dict, List

from aiohttp_retry import Any


class Config:
    def __init__(self):
        self.WEBSITE = os.getenv('WEBSITE', 'nebuia.com')
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', '8000'))
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        self.MESSAGE_API_URL = os.getenv(
            'MESSAGE_API_URL', 'https://api.example.com/messages')
        self.CONTROLLER = {
            "class": "Controller",
            "module": "controllers.default_controller"
        }

    
        self.FUNCTIONS_TO_APPLY: List[Dict[str, Any]] = [
            {'type': 'function', 'function': {'name': 'check_name_valid', 'description': 'check_name_valid(value: str) -> dict - Extract only person name from user input to check validity.\n\n    Args:\n    value (str): Name extracted from user input.\n\n    Returns:\n    dict: A dictionary containing fundamental data.', 'parameters': {
                'type': 'object', 'properties': {'value': {'type': 'string'}}, 'required': ['value']}}},
            {'type': 'function', 'function': {'name': 'check_number_valid', 'description': 'check_number_valid(value: str) -> bool - Validate number from user input to check validity.\n\n    Args:\n    value (str): number extracted.\n\n    Returns:\n    bool: validation boolean result.', 'parameters': {
                'type': 'string', 'properties': {'value': {'type': 'string'}}, 'required': ['value']}}},
            {'type': 'function', 'function': {'name': 'check_amount_to_request', 'description': 'check_amount_to_request(value: str) -> bool - Check max amount of money to request in pesos.\n\n    Args:\n    value (str): amount to request in number.\n\n    Returns:\n    bool: validation boolean result.', 'parameters': {
                'type': 'object', 'properties': {'value': {'type': 'string'}}, 'required': ['value']}}},
            {'type': 'function', 'function': {'name': 'check_email_valid', 'description': 'check_email_valid(value: str) -> bool - validate exact email address extracted from user input.\n\n    Args:\n    value (str): email address extracted from user input.\n\n    Returns:\n    bool: validation boolean result.', 'parameters': {
                'type': 'object', 'properties': {'value': {'type': 'string'}}, 'required': ['value']}}},
            {'type': 'function', 'function': {'name': 'check_otp_valid', 'description': 'check_otp_valid(value: str) -> bool - Check extracted otp code from user input, the code must have 6 numbers.\n\n    Args:\n    value (str): otp code in user input.\n\n    Returns:\n    bool: validation boolean result.', 'parameters': {
                'type': 'object', 'properties': {'value': {'type': 'string'}}, 'required': ['value']}}},
            {'type': 'function', 'function': {'name': 'resend_otp', 'description': 'resend_otp(value: str) -> bool - Resend OTP code to email if users request this.\n\n    Args:\n    value(str): always set to retry.\n\n    Returns:\n    bool: validation boolean result.', 'parameters': {}, 'required': []}}
        ]

        self.MEDIA_FUNCTIONS = {
            "nebuia": {
                "class": "NebuiaFunctions",
                "module": "implementations.nebuia_functions"
            },
        }

        self.CLIENT_CONFIGURATIONS = {
            "default": {
                "ACCOUNT_SID": os.getenv('DEFAULT_ACCOUNT_SID', ''),
                "AUTH_TOKEN": os.getenv('DEFAULT_AUTH_TOKEN', ''),
                "media_functions": "nebuia",
                "functions_to_apply": self.FUNCTIONS_TO_APPLY,
                "INSTITUTION": "NebuIALabs"
            },
        }

    
        self.messages = self.fetch_messages_from_api()

    def get_client_configuration(self, client_id: str) -> dict:
        return self.CLIENT_CONFIGURATIONS.get(client_id, self.CLIENT_CONFIGURATIONS["default"])

    def fetch_messages_from_api(self) -> Dict[str, str]:
        api_response = {
            "WELCOME_MESSAGE": "Hola!, recibes éste mensaje por que tienes una solicitud activa en {institution}. Para iniciar tu proceso selecciona la opción Iniciar. Para más información visita nuestro sitio {website}.",
            "ADDITIONAL_INFO_MESSAGE": "Tambíen puedes preguntar cualquier duda antes de iniciar tu proceso, estámos para atenderte.",
            "START_PROCESS_MESSAGE": "\n\nPara iniciar tu trámite, presiona el botón: *Iniciar proceso* en el mensaje anterior."
        }

        # Uncomment the following lines when you're ready to use a real API
        # try:
        #     response = requests.get(self.MESSAGE_API_URL)
        #     response.raise_for_status()
        #     return response.json()
        # except requests.RequestException as e:
        #     print(f"Error fetching messages from API: {e}")
        #     return api_response  # Use default messages as fallback

        return api_response

    def get_message(self, key: str) -> str:
        """Get a message by its key."""
        return self.messages.get(key, "")

    def format_welcome_message(self) -> str:
        """Format the welcome message with institution and website."""
        return self.get_message("WELCOME_MESSAGE").format(institution=self.INSTITUTION, website=self.WEBSITE)
