import os
import aiohttp
from typing import Callable, Dict, List, Optional, Tuple, Any, Union
from loguru import logger

class APIService:
    def __init__(self, url: str):
        self.url = url
        self.headers = {}

    async def post_stream(self, path: str, body: dict, jwt: str, on_data_callback: Callable[[str, bool], None]) -> Tuple[None, Optional[Exception]]:
        try:
            self.headers['Authorization'] = f'Bearer {jwt}'
            self.headers['Content-Type'] = 'application/json'
            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.url}{path}', json=body, headers=self.headers) as response:
                    async for chunk in response.content.iter_any():
                        decoded_chunk = chunk.decode('utf-8')
                        is_last = False
                        on_data_callback(decoded_chunk, is_last)
                    on_data_callback("", True)
            logger.debug('Finished streaming')
            return None, None
        except Exception as error:
            logger.error(f'Error: {error}')
            return None, error

    async def post(self, path: str, data: Dict[str, Any], jwt: str) -> Tuple[Optional[Dict[str, Any]], Optional[Exception]]:
        try:
            self.headers['Authorization'] = f'Bearer {jwt}'
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.url}{path}", json=data, headers=self.headers) as response:
                    if response.status >= 400:
                        raise Exception(f"HTTP error {response.status}")
                    return await response.json(), None
        except Exception as e:
            return None, e

    async def chat_with_document(self, question: str, uuid: str, messages: List[Dict[str, Union[str, int]]], system: Optional[str], on_data_callback: Callable[[str], None], jwt: str) -> Optional[Dict[str, Any]]:
        try:
            modified = [
                {**item, "page": 0}
                for item in messages
                if item.get("message") and item["message"].strip() != ''
            ]

            body = {
                "uuid": uuid,
                "matches": question,
                "max_results": 3,
                "system": system or '',
                "messages": modified
            }

            response, error = await self.post(f'/instruction/chat/sources', body, jwt)
            if error:
                raise error

            await self.post_stream('/instruction/chat', body, jwt, lambda data, is_last: on_data_callback(data))

            return response
        except Exception as error:
            logger.error('Error getting batches:', error)
            raise

class NebuiaAPIService:
    def __init__(self, ia_url: str, qa_url: str):
        self.api_service = APIService(ia_url)
        self.qa_service = APIService(qa_url)

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        try:
            response, error = await self.api_service.post("/auth/login", {
                "email": email,
                "password": password
            }, None)
            if error:
                raise error
            return response
        except Exception as error:
            logger.error('Error during login:', error)
            raise

    async def simple_question(
        self,
        system: Optional[str],
        messages: List[Dict[str, Union[str, int, List[int]]]],
        web_search: bool,
        on_data_callback: Callable[[str, bool], None],
        jwt: Optional[str]
    ) -> None:
        try:
            modified = [
                {**item, "page": 0}
                for item in messages
                if item.get("message") and item["message"].strip() != ''
            ]
            await self.qa_service.post_stream(
                "/service/chat",
                {
                    "system": system,
                    "messages": modified,
                    "web_search": web_search
                },
                jwt,
                on_data_callback
            )
            return None
        except Exception as error:
            logger.error(f"Error getting batches: {error}")
            raise

    async def chat_with_document(self, question: str, uuid: str, messages: List[Dict[str, Union[str, int]]], system: Optional[str], on_data_callback: Callable[[str], None], jwt: str) -> Optional[Dict[str, Any]]:
        try:
            modified = [
                {**item, "page": 0}
                for item in messages
                if item.get("message") and item["message"].strip() != ''
            ]
            
            body = {
                "uuid": uuid,
                "matches": question,
                "max_results": 3,
                "system": system or '',
                "messages": modified
            }
            
            response, error = await self.qa_service.post(f'/instruction/chat/sources', body, jwt)
            if error:
                raise error
            
            await self.qa_service.post_stream('/instruction/chat', body, jwt, lambda data, is_last: on_data_callback(data))
            
            return response
        except Exception as error:
            logger.error('Error getting batches:', error)
            raise

    async def chat_with_document_wrapper(self, uuid: str, messages: List[Dict[str, Union[str, int]]], question: str) -> Optional[str]:
        try:
            # Login
            login_response = await self.login("miguel@nebuia.com", "rapmundo13")
            jwt = login_response.get("payload")
            if not jwt:
                raise ValueError("JWT not found in login response")

            # Set up the chat
            system_message = "You are a helpful assistant."
            full_response = []

            def on_data(chunk: str):
                full_response.append(chunk)

            # Call chat_with_document
            await self.chat_with_document(question, uuid, messages, system_message, on_data, jwt)

            # Return the full response as a single string
            return "".join(full_response)

        except Exception as e:
            logger.error(f"Error: {e}")
            return None
        

    async def simple_question_wrapper(
        self,
        messages: List[Dict[str, Union[str, int, List[int]]]],
        system: Optional[str] = None,
        web_search: bool = False
    ) -> Optional[str]:
        try:
            # Login
            login_response = await self.login(os.getenv('COPILOT_USER', ''), os.getenv('COPILOT_PASSWORD', ''))
            jwt = login_response.get("payload")
            if not jwt:
                raise ValueError("JWT not found in login response")

            # Set up the chat
            full_response = []

            def on_data(chunk: str, is_last: bool):
                full_response.append(chunk)

            # Call simple_question
            await self.simple_question(system, messages, web_search, on_data, jwt)

            # Return the full response as a single string
            return "".join(full_response)

        except Exception as e:
            logger.error(f"Error in simple_question: {e}")
            return None
