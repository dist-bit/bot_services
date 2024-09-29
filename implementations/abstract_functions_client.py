from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Any

class AbstractClientFunctions(ABC):
    """
    An abstract base class defining the interface for client functions.
    
    This class provides a blueprint for implementing client-specific functions
    related to media tools and OpenAI tools. Subclasses must implement the
    abstract methods to provide concrete implementations.
    """

    @abstractmethod
    def get_media_tools(self) -> Dict[str, Callable]:
        """
        Retrieve a dictionary of media-related tools.

        Returns:
            Dict[str, Callable]: A dictionary where keys are tool names and
            values are callable functions representing the media tools.
        """
        pass

    @abstractmethod
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """
        Retrieve a list of OpenAI tools.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
            represents an OpenAI tool with its properties and configurations.
        """
        pass