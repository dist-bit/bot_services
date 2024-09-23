from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Any

class AbstractClientFunctions(ABC):
    @abstractmethod
    def get_media_tools(self) -> Dict[str, Callable]:
        pass

    @abstractmethod
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        pass