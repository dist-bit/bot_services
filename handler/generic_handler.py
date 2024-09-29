from typing import Dict, Callable, Awaitable

from implementations.response import StructuredResponse

class GenericMediaHandler:
    """
    A generic handler for managing media-related functions and processing steps.
    This class provides a flexible framework for handling various media processing tasks,
    managing function execution, and coordinating communication between system components.
    """

    def __init__(self, 
                 message_handler: Callable[[str, str], None],
                 next_step_handler: Callable[[str, dict], Awaitable[None]]):
        self.message_handler = message_handler
        self.next_step_handler = next_step_handler
        self.function_map: Dict[str, Callable[[dict, str], Awaitable[dict]]] = {}

    def add_function(self, function_name: str, function: Callable[[dict, str], Awaitable[dict]]):
        """
        Adds a new function to the function map.
        
        This method allows for dynamic addition of functions that can be executed by the handler.

        Args:
            function_name (str): The name of the function to be added.
            function (Callable): The function to be executed when called.
        """
        self.function_map[function_name] = function

    async def handle_function(self, function_name: str, step_details: dict, client_id: str):
        """
        Handles the execution of a specific function.

        This method executes the specified function, processes the result, and manages the next steps.

        Args:
            function_name (str): The name of the function to be executed.
            step_details (dict): Details required for the function execution.
            client_id (str): Identifier for the client requesting the function.

        Returns:
            StructuredResponse: The result of the function execution.
        """
        if function_name not in self.function_map:
            return StructuredResponse.error(f"Función no reconocida: {function_name}")

        result: StructuredResponse = await self.function_map[function_name](step_details, client_id)
        self.message_handler(result.message, client_id)
        if result.status:
            await self.next_step_handler(client_id, step_details)
        return result

    async def generate_media_response(self, step_details: dict, client_id: str):
        """
        Generates a media response based on the provided step details.

        This method coordinates the overall process of generating a media response,
        including function execution and message handling.

        Args:
            step_details (dict): Details of the step to be executed, including the function name.
            client_id (str): Identifier for the client requesting the media response.
        """
        function_name = step_details.get("function")
        if not function_name:
            self.message_handler("Función no especificada en step_details", client_id)
            return

        self.message_handler("Procesando su solicitud, por favor espere...", client_id)
        await self.handle_function(function_name, step_details, client_id)
