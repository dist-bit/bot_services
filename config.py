import os
from typing import Dict


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

        # get from api
        self.MEDIA_FUNCTIONS = {
            "nebuia": {
                "class": "NebuiaFunctions",
                "module": "implementations.nebuia_functions"
            },
            "test": {
                "class": "TestFunctions",
                "module": "implementations.test_functions"
            },
        }

        self.CLIENT_CONFIGURATIONS = {
            "19284479697": {
                "ACCOUNT_SID": os.getenv('DEFAULT_ACCOUNT_SID', ''),
                "AUTH_TOKEN": os.getenv('DEFAULT_AUTH_TOKEN', ''),
                "media_functions": "nebuia",
                "institution": "NebuIALabs",
                "context_uuid": "aa9dd496-9bdd-47b0-af99-e66f0df314b1",
                "phone_number": "19284479697"
            },
            "test": {
                "ACCOUNT_SID": os.getenv('DEFAULT_ACCOUNT_SID', ''),
                "AUTH_TOKEN": os.getenv('DEFAULT_AUTH_TOKEN', ''),
                "media_functions": "test",
                "institution": "NebuIALabs",
                "context_uuid": "aa9dd496-9bdd-47b0-af99-e66f0df314b1",
                "phone_number": "19284479697"
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

    def format_welcome_message(self, institution: str) -> str:
        """Format the welcome message with institution and website."""
        return self.get_message("WELCOME_MESSAGE").format(institution=institution, website=self.WEBSITE)
