"""
Integration tests for the complete Agent API Framework.
"""

import pytest
from fastapi.testclient import TestClient
from agent_api_framework import (
    AgentHTTPHandler, 
    AgentWSHandler, 
    AppConfig, 
    HTTPRouteConfig, 
    WSRouteConfig, 
    create_agent_app
)
from fastapi import Request, WebSocket
from fastapi.responses import JSONResponse
import json
import asyncio


class IntegrationHTTPHandler(AgentHTTPHandler):
    def __init__(self):
        self.request_count = 0
    
    async def handle(self, request: Request) -> JSONResponse:
        self.request_count += 1
        
        if request.method == "GET":
            return JSONResponse({
                "message": "Hello from integration test",
                "request_count": self.request_count,
                "path": str(request.url.path)
            })
        elif request.method == "POST":
            try:
                body = await request.json()
                return JSONResponse({
                    "received": body,
                    "request_count": self.request_count
                })
            except:
                return JSONResponse({
                    "error": "Invalid JSON",
                    "request_count": self.request_count
                }, status_code=400)


class IntegrationWSHandler(AgentWSHandler):
    def __init__(self):
        self.connection_count = 0
        self.message_count = 0
    
    async def handle(self, websocket: WebSocket):
        self.connection_count += 1
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "connection_id": self.connection_count,
            "message": "Connected to integration test WebSocket"
        }))
        
        try:
            while True:
                message = await websocket.receive_text()
                self.message_count += 1
                
                try:
                    data = json.loads(message)
                    command = data.get("command")
                    
                    if command == "echo":
                        response = {
                            "type": "echo",
                            "data": data.get("data"),
                            "message_count": self.message_count
                        }
                    elif command == "stats":
                        response = {
                            "type": "stats",
                            "connection_count": self.connection_count,
                            "message_count": self.message_count
                        }
                    else:
                        response = {
                            "type": "error",
                            "message": f"Unknown command: {command}"
                        }
                    
                    await websocket.send_text(json.dumps(response))
                    
                except json.JSONDecodeError:
                    # Handle plain text messages
                    response = {
                        "type": "text_echo",
                        "message": message,
                        "message_count": self.message_count
                    }
                    await websocket.send_text(json.dumps(response))
                    
        except Exception as e:
            print(f"WebSocket error: {e}")


@pytest.fixture
def integration_app():
    """Create a complete integration test app."""
    http_handler = IntegrationHTTPHandler()
    ws_handler = IntegrationWSHandler()
    
    config = AppConfig(
        title="Integration Test API",
        description="Full integration test for Agent API Framework",
        version="1.0.0-test",
        http_routes=[
            HTTPRouteConfig(
                path="/api/integration",
                methods=["GET", "POST"],
                handler=http_handler,
                tags=["integration"],
                summary="Integration test endpoint"
            )
        ],
        ws_routes=[
            WSRouteConfig(
                path="/ws/integration",
                handler=ws_handler,
                name="integration_websocket"
            )
        ],
        port=8001,
        log_level="debug"
    )
    
    return create_agent_app(config)


@pytest.fixture
def integration_client(integration_app):
    """Create a test client for integration tests."""
    return TestClient(integration_app)


def test_full_http_integration(integration_client):
    """Test complete HTTP functionality."""
    # Test GET request
    response = integration_client.get("/api/integration")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello from integration test"
    assert data["request_count"] == 1
    assert data["path"] == "/api/integration"
    
    # Test POST request with JSON
    post_data = {"test": "data", "number": 42}
    response = integration_client.post("/api/integration", json=post_data)
    assert response.status_code == 200
    data = response.json()
    assert data["received"] == post_data
    assert data["request_count"] == 2
    
    # Test health endpoint
    response = integration_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_full_websocket_integration(integration_client):
    """Test complete WebSocket functionality."""
    with integration_client.websocket_connect("/ws/integration") as websocket:
        # Receive welcome message
        welcome = websocket.receive_text()
        welcome_data = json.loads(welcome)
        assert welcome_data["type"] == "welcome"
        assert welcome_data["connection_id"] == 1
        
        # Test echo command
        websocket.send_text(json.dumps({
            "command": "echo",
            "data": {"test": "echo_data"}
        }))
        
        response = websocket.receive_text()
        response_data = json.loads(response)
        assert response_data["type"] == "echo"
        assert response_data["data"] == {"test": "echo_data"}
        assert response_data["message_count"] == 1
        
        # Test stats command
        websocket.send_text(json.dumps({"command": "stats"}))
        
        response = websocket.receive_text()
        response_data = json.loads(response)
        assert response_data["type"] == "stats"
        assert response_data["connection_count"] == 1
        assert response_data["message_count"] == 2
        
        # Test plain text message
        websocket.send_text("Hello WebSocket!")
        
        response = websocket.receive_text()
        response_data = json.loads(response)
        assert response_data["type"] == "text_echo"
        assert response_data["message"] == "Hello WebSocket!"
        assert response_data["message_count"] == 3
        
        # Test unknown command
        websocket.send_text(json.dumps({"command": "unknown"}))
        
        response = websocket.receive_text()
        response_data = json.loads(response)
        assert response_data["type"] == "error"
        assert "Unknown command" in response_data["message"]


def test_concurrent_connections(integration_client):
    """Test multiple concurrent WebSocket connections."""
    connections = []
    
    try:
        # Open multiple connections
        for i in range(3):
            ws = integration_client.websocket_connect("/ws/integration")
            connections.append(ws.__enter__())
        
        # Test that each connection gets a unique ID
        connection_ids = []
        for ws in connections:
            welcome = ws.receive_text()
            welcome_data = json.loads(welcome)
            connection_ids.append(welcome_data["connection_id"])
        
        # All connection IDs should be unique and sequential
        assert len(set(connection_ids)) == 3
        assert sorted(connection_ids) == [1, 2, 3]
        
        # Test messaging on each connection
        for i, ws in enumerate(connections):
            ws.send_text(json.dumps({"command": "stats"}))
            response = ws.receive_text()
            response_data = json.loads(response)
            assert response_data["connection_count"] == 3
    
    finally:
        # Clean up connections
        for ws in connections:
            try:
                ws.__exit__(None, None, None)
            except:
                pass


def test_api_documentation(integration_client):
    """Test that API documentation is available."""
    # Test OpenAPI schema
    response = integration_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Integration Test API"
    assert schema["info"]["version"] == "1.0.0-test"
    
    # Test Swagger UI
    response = integration_client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()


def test_cors_functionality(integration_client):
    """Test CORS functionality."""
    # Test preflight request
    response = integration_client.options(
        "/api/integration",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers