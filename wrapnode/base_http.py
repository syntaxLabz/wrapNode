"""
Base HTTP handler abstract class for agent endpoints.
"""

from abc import ABC, abstractmethod
from fastapi import Request
from fastapi.responses import JSONResponse


class AgentHTTPHandler(ABC):
    """
    Abstract base class for HTTP request handlers.
    
    All agent HTTP handlers must inherit from this class and implement
    the handle method to process incoming HTTP requests.
    """
    
    @abstractmethod
    async def handle(self, request: Request) -> JSONResponse:
        """
        Handle an incoming HTTP request.
        
        Args:
            request: The FastAPI Request object containing the HTTP request data
            
        Returns:
            JSONResponse: The response to send back to the client
            
        Raises:
            NotImplementedError: If the method is not implemented by the subclass
        """
        pass
    
    async def on_startup(self) -> None:
        """
        Optional startup hook called when the handler is initialized.
        Override this method to perform any setup operations.
        """
        pass
    
    async def on_shutdown(self) -> None:
        """
        Optional shutdown hook called when the application is shutting down.
        Override this method to perform any cleanup operations.
        """
        pass