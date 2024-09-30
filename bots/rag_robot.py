from typing import Any, Dict, Optional
from bots.copilot import NebuiaAPIService
from engine.engine import Engine


class Promoter:
    def __init__(self, institution: str, uuid: str) -> None:
        self.engine = Engine()
        self.institution = institution
        self.uuid = uuid
        self.system_first_contact = f"Eres un asistente virtual para {self.institution}."
        self.system = f"Eres un asistente virtual de para {self.institution}, deberás responder al usuario con la información dada, no respondas información que no conoces, limitate al contexto dado y responde en tercera persona."
        self.nebuia_service = NebuiaAPIService('https://ia.nebuia.com/api/v1', 'https://qa.nebuia.com/api/v1')
        pass

    def dict_to_string(self, data: Optional[Dict[str, Any]]) -> str:
        if data is None:
            return "None"
        
        return "\n".join(f"{key}: {value}" for key, value in data.items())

    def format_message(self, user_input, step, summary, data=None):
        base_message = f"Se obtuvo el siguiente mensaje del usuario: {user_input}."
        data_info = f"Siempre usa los siguientes datos para tu respuesta:\n\n{self.dict_to_string(data)}\n" if data else ""
        context = f"Al realizar el paso: {step} y este es su resumen: {summary}."
        instructions = ("Mantienes una conversación activa con el usuario, "
                        "evita decir Hola, Bienvenido, o cualquier otro tipo de saludo, tu objetivo es "
                        "responder la duda del usuario basandote en el contexto dado, no involucres otros pasos. "
                        "Se muy corto en tu respuesta.")

        return f"{base_message}\n{data_info}\n{context}\n{instructions}"

    def set_institution(self, institution: str):
        self.institution = institution

    async def generate_hello(self) -> str:
        messages = [
            {
                "role": "user",
                "message": f"Presentate. Se educado y haz sentir al cliente seguro, sólo explicale que le ayudarás a resolver sus dudas y estás a su disposición",
            }
        ]

        response = await self.nebuia_service.simple_question_wrapper(messages, self.system_first_contact)
        return response


    async def generic_conversation(self, msg) -> str:
        doc_messages = []
        doc_question = msg

        doc_response = await self.nebuia_service.chat_with_document_wrapper(self.uuid, doc_messages, doc_question)
        return doc_response
    

    async def generate_instruction(self, step: str, summary: str) -> str:
        messages = [
            {
                "role": "user",
                "message": f"Genera un mensaje donde solicites: {step}, el cual es necesario para: {summary}.",
            }
        ]

        system = "Sigue ayudando al cliente mediante chat a concluir su proceso, evita decir Hola, Buen dia, o cualquier otro tipo de saludo."
        response = await self.nebuia_service.simple_question_wrapper(messages, system)
        return response

    async def generate_instruction_with_explain(self, 
                                                step: str, 
                                                summary: str, 
                                                user_input: str = "", 
                                                data: Optional[Dict[str, Any]] = None) -> str:

        doc_messages = [
            {
                "role": "system",
                "message": self.format_message(user_input, step, summary, data)
            }
        ]

        doc_response = await self.nebuia_service.chat_with_document_wrapper(self.uuid, doc_messages, user_input)
        return doc_response