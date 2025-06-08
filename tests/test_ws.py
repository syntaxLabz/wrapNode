"""
Tests for WebSocket handlers and routing.
"""

import pytest
from fastapi.testclient import TestClient
from agent_api_framework import AgentWSHandler, AppConfig, WSRouteConfig, create_agent_app
from fastapi import WebSocket
import json


class TestWSHandler(AgentWSHandler):
    async def handle(self, websocket: WebSocket):
        try:
            while True:
                message = await websocket.receive_text()
                await websocket.send_text(f"Echo: {message}")
        except:
            pass


class TestWSHandlerWithHooks(AgentWSHandler):
    def __init__(self):
        self.connect_called = False
        self.disconnect_called = False
        self.startup_called = False
        self.shutdown_called = False
    
    async def handle(self, websocket: WebSocket):
        await websocket.send_text(json.dumps({
            "connect_called": self.connect_called,
            "startup_called": self.startup_called
        }))
        
        try:
            while True:
                message = await websocket.receive_text()
                await websocket.send_text(f"Received: {message}")
        except:
            pass
    
    async def on_connect(self, websocket: WebSocket) -> bool:
        self.connect_called = True
        return True
    
    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        self.disconnect_called = True
    
    async def on_startup(self):
        self.startup_called = True
    
    async def on_shutdown(self):
        self.shutdown_called = True


class TestWSHandlerRejectConnection(AgentWSHandler):
    async def handle(self, websocket: WebSocket):
        pass  # Should not be called
    
    async def on_connect(self, websocket: WebSocket) -> bool:
        return False  # Reject connection


@pytest.fixture
def test_app():
    """Create a test FastAPI app with WebSocket routes."""
    config = AppConfig(
        ws_routes=[
            WSRouteConfig(
                path="/ws/test",
                handler=TestWSHandler()
            )
        ]
    )
    return create_agent_app(config)


@pytest.fixture
def client(test_app):
    """Create a test client."""
    return TestClient(test_app)


def test_websocket_connection(client):
    """Test basic WebSocket connection and messaging."""
    with client.websocket_connect("/ws/test") as websocket:
        websocket.send_text("Hello")
        data = websocket.receive_text()
        assert data == "Echo: Hello"
        
        websocket.send_text("World")
        data = websocket.receive_text()
        assert data == "Echo: World"


def test_websocket_hooks():
    """Test WebSocket lifecycle hooks."""
    handler = TestWSHandlerWithHooks()
    config = AppConfig(
        ws_routes=[
            WSRouteConfig(
                path="/ws/test",
                handler=handler
            )
        ]
    )
    
    app = create_agent_app(config)
    client = TestClient(app)
    
    with client.websocket_connect("/ws/test") as websocket:
        # Receive initial message with hook status
        data = websocket.receive_text()
        message = json.loads(data)
        assert message["connect_called"] is True
        assert message["startup_called"] is True
        
        websocket.send_text("test")
        response = websocket.receive_text()
        assert response == "Received: test"
    
    # After connection closes, disconnect should be called
    assert handler.disconnect_called is True


def test_websocket_connection_rejection():
    """Test WebSocket connection rejection."""
    config = AppConfig(
        ws_routes=[
            WSRouteConfig(
                path="/ws/reject",
                handler=TestWSHandlerRejectConnection()
            )
        ]
    )
    
    app = create_agent_app(config)
    client = TestClient(app)
    
    # Connection should be rejected
    with pytest.raises(Exception):  # WebSocket connection will fail
        with client.websocket_connect("/ws/reject"):
            pass


def test_websocket_route_config():
    """Test WebSocket route configuration."""
    handler = TestWSHandler()
    
    # Test path normalization
    config = WSRouteConfig(
        path="ws/test",  # Missing leading slash
        handler=handler
    )
    assert config.path == "/ws/test"
    
    # Test with name
    config_with_name = WSRouteConfig(
        path="/ws/named",
        handler=handler,
        name="test_websocket"
    )
    assert config_with_name.name == "test_websocket"