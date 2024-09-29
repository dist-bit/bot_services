from typing import Dict, Callable, Awaitable

from implementations.response import StructuredResponse

class GenericMediaHandler:
    def __init__(self, 
                 message_handler: Callable[[str, str], None],
                 next_step_handler: Callable[[str, dict], Awaitable[None]]):
        self.message_handler = message_handler
        self.next_step_handler = next_step_handler
        self.function_map: Dict[str, Callable[[dict, str], Awaitable[dict]]] = {}

    def add_function(self, function_name: str, function: Callable[[dict, str], Awaitable[dict]]):
        """Añade una nueva función al mapa de funciones."""
        self.function_map[function_name] = function

    async def handle_function(self, function_name: str, step_details: dict, client_id: str):
        """Maneja la ejecución de una función específica."""
        if function_name not in self.function_map:
            return StructuredResponse.error(f"Función no reconocida: {function_name}")

        result = await self.function_map[function_name](step_details, client_id)
        self.message_handler(result.message, client_id)
        if result.status:
            await self.next_step_handler(client_id, step_details)
        return result

    async def generate_media_response(self, step_details: dict, client_id: str):
        """Genera una respuesta de media basada en los detalles del paso."""
        function_name = step_details.get("function")
        if not function_name:
            self.message_handler("Función no especificada en step_details", client_id)
            return

        self.message_handler("Procesando su solicitud, por favor espere...", client_id)
        await self.handle_function(function_name, step_details, client_id)
