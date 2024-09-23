from bots.copilot import NebuiaAPIService
from engine.engine import Engine


class Promoter:
    def __init__(self, institution: str) -> None:
        self.engine = Engine()
        self.institution = institution
        self.system_first_contact = f"Eres un asistente virtual para {self.institution}, llamado NebuIA."
        self.system = f"Eres un asistente virtual de para {self.institution}, llamado Julieth, deberás responder al usuario con la información dada, no respondas información que no conoces, limitate al contexto dado y responde en tercera persona."
        self.nebuia_service = NebuiaAPIService('https://ia.nebuia.com/api/v1', 'https://qa.nebuia.com/api/v1')
        pass

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
        uuid = "aa9dd496-9bdd-47b0-af99-e66f0df314b1"
        doc_messages = []
        doc_question = msg

        doc_response = await self.nebuia_service.chat_with_document_wrapper(uuid, doc_messages, doc_question)
        return doc_response
    

    async def generate_instruction(self, step: str, summary: str, is_valid: bool = True, retry_msg: str = "") -> str:
        messages = [
            {
                "role": "user",
                "message": f"Genera un mensaje donde solicites: {step}, el cual es necesario para: {summary}." if is_valid else f"Solicita nuevamente: {step}. Ya que la información ingresada no fue correcta. Información del paso: {summary}. Error: {retry_msg}",
            }
        ]

        system = "Sigue ayudando al cliente mediante chat a concluir su proceso, evita decir Hola, Buen dia, o cualquier otro tipo de saludo."
        response = await self.nebuia_service.simple_question_wrapper(messages, system)
        return response

    async def generate_instruction_with_explain(self, step: str, summary: str, is_valid: bool = False, retry_msg: str = "") -> str:
        #q =  "Responde de acuerdo a la siguiente información: {context}.\nPregunta del usuario: {retry_msg}.\nEl paso de verificación que se está realizando es: {step}.\nRecuerda que eres de soporte, y mantienes una conversación activa con el usuario, evita decir Hola, Bienveido, o cualquier otro tipo de saludo, tu objetivo es responder la duda del usuario basandote en el contexto dado, no involucres otros pasos. Se muy corto en tu respuesta.".format(context="{context}", retry_msg=retry_msg, step=step
        q =  "{retry_msg}.\nEl paso de verificación que se está realizando es: {step} y este es su resumen: {summary}.\nRecuerda que eres de soporte, y mantienes una conversación activa con el usuario, evita decir Hola, Bienveido, o cualquier otro tipo de saludo, tu objetivo es responder la duda del usuario basandote en el contexto dado, no involucres otros pasos. Se muy corto en tu respuesta.".format(context="{context}", retry_msg=retry_msg, step=step, summary=summary)
        uuid = "70e12f41-b98d-4640-bb83-98004815c3e7"
        match = retry_msg

  
        uuid = "aa9dd496-9bdd-47b0-af99-e66f0df314b1"
        doc_messages = [
            {
                "role": "system",
                "message": q
            }
        ]

        doc_response = await self.nebuia_service.chat_with_document_wrapper(uuid, doc_messages, match)

        return doc_response