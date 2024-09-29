from typing import Any, Dict, List, Optional
from handler.text_handler import TextInputHandler
from implementations.abstract_functions_client import AbstractClientFunctions
from handler.generic_handler import GenericMediaHandler
from loguru import logger

class Controller:
    def __init__(self, client, db, promoter_robot, media_functions, tool_caller, client_config: dict):
        self.client = client
        self.db = db
        self.promoter_robot = promoter_robot
        self.tool_caller = tool_caller
        self.client_config = client_config
        self.media_functions: Optional[AbstractClientFunctions] = None
        self.media_handler: Optional[GenericMediaHandler] = None
        self.initialize_media_handler(media_functions)
        self.text_input_handler = TextInputHandler(
            tool_caller=self.tool_caller,
            message_sender=self.message,
            description_instruction_caller=self.call_description_instruction,
            next_step_handler=self.next_step,
            report_getter=self.get_report_by_client
        )

    def initialize_media_handler(self, media_functions: AbstractClientFunctions, function_names: List[str] = None):
        self.media_functions = media_functions
        self.media_handler = GenericMediaHandler(
            message_handler=self.message,
            next_step_handler=self.next_step
        )
        all_functions = self.media_functions.get_media_tools()
        if function_names:
            for name in function_names:
                if name in all_functions:
                    self.media_handler.add_function(name, all_functions[name])
                else:
                    logger.warning(f"Warning: Function '{name}' not found in media_functions")
        else:
            for name, func in all_functions.items():
                self.media_handler.add_function(name, func)

    async def generate_media_response(self, step_details, client_id):
        if not self.media_handler:
            raise ValueError("Media handler not initialized. Call initialize_media_handler first.")
        await self.media_handler.generate_media_response(step_details, client_id)

    def message(self, msg: str, client_id: str):
        self.client.messages.create(
            from_=f'whatsapp:+{self.client_config.get("phone_number")}',
            body=msg,
            to=f"whatsapp:+{client_id}"
        )

    async def next_step(self, client_id: str, step_details: dict):
        self.db.mark_step_as_complete(client_id, step_details["function"])
        next_step_details = self.db.get_step_by_client(client_id)
        if next_step_details is not None:
            instruction = await self.call_description_instruction(next_step_details, user_input="")
            self.message(instruction, client_id)
        else:
            self.message("Has terminado.", client_id)

    def get_to_client(self, id_client):
        to = self.db.client_exist(id_client)
        return to

    def init_first_contact(self, to: str, hello: str, instruction: str):
        number = to
        self.message(hello, number)
        self.message(instruction, number)

    def get_report_by_client(self, client_id: str):
        return self.get_to_client(client_id)["report"]

    async def call_description_instruction(self, step, user_input: str, data: Optional[Dict[str, Any]] = None):
        if user_input == "":
            return await self.promoter_robot.generate_instruction(step=step["value"], summary=step["summary"])
        return await self.promoter_robot.generate_instruction_with_explain(step=step["value"], summary=step["summary"], user_input=user_input, data=data)

    async def generic_conversation(self, msg: str = ''):
        generate_instruction = await self.promoter_robot.generic_conversation(msg)
        return generate_instruction

    async def handle_text_input(self, user_response: str, step_details: dict, client_id: str):
        await self.text_input_handler.handle_text_input(user_response, step_details, client_id)

    def process_media(self, request, step_details: dict, client_id: str):
        logger.info(request)
        media_url = request.form.get('MediaUrl0')
        self.db.add_image_to_step(
            client_id=client_id, unique_function_name=step_details["function"], image_url=media_url)

    async def handle_media_upload(self, step_details: dict, client_id: str):
        if step_details["require_images"]:
            step_details = self.db.get_step_by_client(client_id)
            await self.generate_media_response(step_details, client_id)
        else:
            self.message("Este paso no requiere de multimedia", client_id=client_id)

    async def handle_button_message(self, client_id: str):
        self.db.set_steps_to_client(client_id=client_id)
        step_details = self.db.get_step_by_client(client_id)

        hello = await self.promoter_robot.generate_hello()
        instruction = await self.call_description_instruction(step=step_details, user_input="")
        self.init_first_contact(client_id, hello=hello, instruction=instruction)

    async def handle_empty_steps(self, client_id: str, user_response: str):
        instruction = await self.generic_conversation(msg=user_response)
        #instruction += "\n\nPara iniciar tu trámite, presiona el botón: *Iniciar proceso* en el mensaje anterior."
        self.message(instruction, client_id=client_id)