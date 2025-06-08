"""
Base WebSocket handler abstract class for agent endpoints.
"""

from abc import ABC, abstractmethod
from fastapi import WebSocket


class AgentWSHandler(ABC):
    """
    Abstract base class for WebSocket connection handlers.
    
    All agent WebSocket handlers must inherit from this class and implement
    the handle method to process WebSocket connections.
    """
    
    @abstractmethod
    async def handle(self, websocket: WebSocket) -> None:
        """
        Handle a WebSocket connection.
        
        Args:
            websocket: The FastAPI WebSocket object for the connection
            
        Note:
            This method should accept the WebSocket connection and handle
            the entire lifecycle of the connection, including receiving
            and sending messages.
        """
        pass
    
    async def on_connect(self, websocket: WebSocket) -> bool:
        """
        Optional hook called before accepting a WebSocket connection.
        
        Args:
            websocket: The WebSocket connection to evaluate
            
        Returns:
            bool: True to accept the connection, False to reject it
        """
        return True
    
    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        """
        Optional hook called when a WebSocket connection is closed.
        
        Args:
            websocket: The WebSocket connection that was closed
            close_code: The close code indicating why the connection was closed
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