from typing import Dict, Optional
from loguru import logger

from implementations.response import StructuredResponse

class TextInputHandler:
    """
    Handles text input from users and processes it according to the current step in the workflow.
    """

    def __init__(self, tool_caller, message_sender, description_instruction_caller, next_step_handler, report_getter):
        """
        Initialize the TextInputHandler with necessary dependencies.

        :param tool_caller: Function to call tools based on user input
        :param message_sender: Function to send messages to the client
        :param description_instruction_caller: Function to get instructions for the next step
        :param next_step_handler: Function to handle the next step in the workflow
        :param report_getter: Function to get the report ID for a client
        """
        self.tool_caller = tool_caller
        self.message_sender = message_sender
        self.description_instruction_caller = description_instruction_caller
        self.next_step_handler = next_step_handler
        self.report_getter = report_getter

    async def handle_text_input(self, user_response: str, step_details: Dict, client_id: str) -> None:
        """
        Main method to handle text input from the user.

        :param user_response: The text input from the user
        :param step_details: Details about the current step in the workflow
        :param client_id: Unique identifier for the client
        """
        if step_details["require_images"]:
            await self._handle_image_requirement(step_details, user_response, client_id)
            return

        report_id = self.report_getter(client_id)
        tool_response = self._get_tool_response(user_response, step_details, report_id)

        if tool_response is None:
            await self._handle_no_tool_response(step_details, user_response, client_id)
            return

        response = self._extract_response_content(tool_response)
        if response is None:
            await self._handle_empty_response(step_details, user_response, client_id)
            return

        if response.status:
            await self._handle_successful_response(response, step_details, client_id, user_response)
        else:
            self._handle_failed_response(response, client_id)

    async def _handle_image_requirement(self, step_details: Dict, user_response: str, client_id: str) -> None:
        """
        Handle steps that require image input.

        :param step_details: Details about the current step
        :param user_response: The text input from the user
        :param client_id: Unique identifier for the client
        """
        instruction = await self.description_instruction_caller(step_details, user_input=user_response)
        self.message_sender(instruction, client_id=client_id)

    def _get_tool_response(self, user_response: str, step_details: Dict, report_id: str) -> Optional[list]:
        """
        Get the response from the tool based on user input.

        :param user_response: The text input from the user
        :param step_details: Details about the current step
        :param report_id: ID of the current report
        :return: The response from the tool, or None if no response
        """
        tool_response = self.tool_caller.process_input_tool(
            user_response, step_details["available_functions"], report_id)
        logger.info(f"tool response: {tool_response}")
        return tool_response

    def _extract_response_content(self, tool_response: list) -> Optional[object]:
        """
        Extract the content from the tool response.

        :param tool_response: The response from the tool
        :return: The content of the response, or None if the response is empty
        """
        return tool_response[0]["content"] if tool_response else None

    async def _handle_no_tool_response(self, step_details: Dict, user_response: str, client_id: str) -> None:
        """
        Handle the case when there's no response from the tool.

        :param step_details: Details about the current step
        :param user_response: The text input from the user
        :param client_id: Unique identifier for the client
        """
        instruction = await self.description_instruction_caller(step_details, user_input=user_response)
        self.message_sender(instruction, client_id=client_id)

    async def _handle_empty_response(self, step_details: Dict, user_response: str, client_id: str) -> None:
        """
        Handle the case when the response from the tool is empty.

        :param step_details: Details about the current step
        :param user_response: The text input from the user
        :param client_id: Unique identifier for the client
        """
        instruction = await self.description_instruction_caller(step_details, user_input=user_response)
        self.message_sender(instruction, client_id=client_id)

    async def _handle_successful_response(self, response: StructuredResponse, step_details: Dict, client_id: str, user_response: str) -> None:
        """
        Handle a successful response from the tool.

        :param response: The structured response from the tool
        :param step_details: Details about the current step
        :param user_response: The text input from the user
        :param client_id: Unique identifier for the client
        """
        if response.response_with_llm:
            data = response.data if response.data is not None else None
            user_input = user_response if data else response.message
            instruction = await self.description_instruction_caller(step_details, user_input=user_input, data=data)
        else:
            instruction = response.message
        
        self.message_sender(instruction, client_id=client_id)

        if response.mark_as_complete:
            await self.next_step_handler(client_id=client_id, step_details=step_details)

    def _handle_failed_response(self, response: StructuredResponse, client_id: str) -> None:
        """
        Handle a failed response from the tool.

        :param response: The structured response from the tool
        :param client_id: Unique identifier for the client
        """
        self.message_sender(response.message, client_id=client_id)