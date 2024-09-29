from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class StructuredResponse:
    status: bool
    message: str
    mark_as_complete: bool
    data: Optional[Dict[str, Any]] = None
    response_with_llm: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the structured response to a dictionary.
        
        Returns:
            Dict: Dictionary representing the structured response.
        """
        response_dict = asdict(self)
        if self.data is None:
            del response_dict['data']
        return response_dict

    @classmethod
    def error(cls, message: str, response_with_llm = False) -> 'StructuredResponse':
        """
        Create an error response.
        
        Args:
            message: error message.
        
        Returns:
            StructuredResponse: A StructuredResponse instance with status False.
        """
        return cls(status=False, message=message, response_with_llm = response_with_llm)

    @classmethod
    def success(cls, message: str, mark_as_complete = True, data: Optional[Dict[str, Any]] = None, response_with_llm = False) -> 'StructuredResponse':
        """
        Create a success response.
        
        Args:
            message: success message.
            data : Additional data for the response.
        
        Returns:
            StructuredResponse: A StructuredResponse instance with status True.
        """
        return cls(status=True, message=message, data=data, response_with_llm = response_with_llm, mark_as_complete=mark_as_complete)