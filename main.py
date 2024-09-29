import importlib
import logging
from dotenv import load_dotenv
from loguru import logger
from config import Config
from engine.model_calling import ToolCaller
from bots.promoter_robot import Promoter
from database.mongo import MongoDB
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request
from twilio.rest import Client
from typing import Dict, Any
import json
import asyncio
from typing import Dict, Any
import requests

from implementations.abstract_functions_client import AbstractClientFunctions

load_dotenv()

class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


class WhatsAppBot:
    def __init__(self, config: Config):
        self.config = config
        self.controllers: Dict[str, Any] = {}
        self.media_functions: Dict[str, Any] = {}
        self.setup_components()
        self.setup_flask_app()

    def setup_components(self):
        self.db = MongoDB()

    def get_session(self, client_config: dict) -> requests.Session:
        session = requests.Session()
        session.auth = (client_config.get('ACCOUNT_SID'), client_config.get('AUTH_TOKEN'))
        return session
    
    def get_bot_client(self, client_config: dict) -> Client:
        return Promoter(institution=client_config.get('INSTITUTION'))

    def get_client(self, client_config: dict) -> Client:
        return Client(client_config.get('ACCOUNT_SID'), client_config.get('AUTH_TOKEN'))

    def get_client_tools(self, client_config: dict) -> AbstractClientFunctions:
        media_functions_name = client_config["media_functions"]
        media_functions_info = self.config.MEDIA_FUNCTIONS[media_functions_name]
        module = importlib.import_module(media_functions_info["module"])
        media_functions_class = getattr(module, media_functions_info["class"])
        session = self.get_session(client_config)
        return media_functions_class(self.db, session)


    def get_tool_caller(self, client_functions: AbstractClientFunctions) -> ToolCaller:
        return ToolCaller(
            client_functions=client_functions
        )

    def get_controller(self, client_id: str) -> Any:
        client_config = self.config.get_client_configuration(client_id)
        controller_info = self.config.CONTROLLER
        module = importlib.import_module(controller_info["module"])
        controller_class = getattr(module, controller_info["class"])

        client_functions = self.get_client_tools(client_config)

        tool_caller = self.get_tool_caller(client_functions)
        client = self.get_client(client_config)

        promoter = self.get_bot_client(client_config)
        
        return controller_class(
            client=client,
            db=self.db,
            promoter_robot=promoter,
            media_functions=client_functions,
            tool_caller=tool_caller,
            client_config=client_config
        )

    def reply_whatsapp(self):
        client_id = request.values.get('WaId')
        user_response = request.values.get('Body')

        implementation = "521999999999"  # Este valor debería ser dinámico basado en el cliente
        controller = self.get_controller(implementation)

        message_type = request.values.get("MessageType")
        print(request.values.get("To"))
        logger.info(f"Received message from {client_id}")

        if message_type == 'button':
            asyncio.run(controller.handle_button_message(client_id))
            return str(MessagingResponse())

        client_local = self.db.client_exist(client_id=client_id)
        if len(client_local["steps"]) == 0:
            asyncio.run(controller.handle_empty_steps(client_id, user_response))
            return str(MessagingResponse())

        media = request.values.get("NumMedia")
        num_media = int(media) if media is not None else 0
        step_details = self.db.get_step_by_client(client_id)

        if num_media > 0 and step_details["require_images"]:
            controller.process_media(request, step_details, client_id)
            asyncio.run(controller.handle_media_upload(step_details, client_id))
        else:
            asyncio.run(controller.handle_text_input(user_response, step_details, client_id))

        return str(MessagingResponse())

    def setup_flask_app(self):
        self.app = Flask(__name__)
        self.app.config.from_object(self.config)
        self.app.logger.addHandler(InterceptHandler())
        CORS(self.app)

        self.setup_routes()

    def signed_notification(self):
        return json.dumps({"status": True, "payload": True})

    def get_status(self):
        return json.dumps({"status": True, "payload": True})

    def remove_contact(self):
        data = request.json
        to = f"521{data['client_id']}"
        self.db.remove_item(to)
        return json.dumps({"status": True, "payload": True})

    def init_contact(self):
        data = request.json
        to = f"521{data['client_id']}"

        client = self.db.client_exist(to)

        implementation = "521999999999"
        controller = self.get_controller(implementation)

        if client is None:
            steps = data['steps']
            nebuia_report = data['nebuia_report']

            self.db.create_client(to, report=nebuia_report)
            self.db.set_steps_to_client_temporal(to, steps)

        institution = controller.client_config.get('INSTITUTION')
        welcome_msg = self.config.format_welcome_message(institution=institution)
 
        controller.message(welcome_msg, to)
        controller.message(self.config.get_message(
            "ADDITIONAL_INFO_MESSAGE"), to)
        return json.dumps({"status": True, "payload": True})
    

    def setup_routes(self):
        self.app.route("/notification/signed",
                       methods=["GET", "POST"])(self.signed_notification)
        self.app.route("/status", methods=["GET", "POST"])(self.get_status)
        self.app.route("/remove/contact",
                       methods=["GET", "POST"])(self.remove_contact)
        self.app.route("/init/contact",
                       methods=["GET", "POST"])(self.init_contact)
        self.app.route(
            "/whatsapp", methods=["GET", "POST"])(self.reply_whatsapp)

    @staticmethod
    def run_async(coroutine):
        def wrapper(*args, **kwargs):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coroutine(*args, **kwargs))
            loop.close()
        return wrapper

    def run(self):
        self.app.run(host=self.config.HOST, port=self.config.PORT,
                     debug=self.config.DEBUG)


if __name__ == '__main__':
    config = Config()
    bot = WhatsAppBot(config)
    bot.run()
