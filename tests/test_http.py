"""
Tests for HTTP handlers and routing.
"""

import pytest
from fastapi.testclient import TestClient
from agent_api_framework import AgentHTTPHandler, AppConfig, HTTPRouteConfig, create_agent_app
from fastapi import Request
from fastapi.responses import JSONResponse


class TestHTTPHandler(AgentHTTPHandler):
    async def handle(self, request: Request) -> JSONResponse:
        return JSONResponse({"test": "success", "method": request.method})


class TestHTTPHandlerWithStartup(AgentHTTPHandler):
    def __init__(self):
        self.startup_called = False
        self.shutdown_called = False
    
    async def handle(self, request: Request) -> JSONResponse:
        return JSONResponse({"startup_called": self.startup_called})
    
    async def on_startup(self):
        self.startup_called = True
    
    async def on_shutdown(self):
        self.shutdown_called = True


@pytest.fixture
def test_app():
    """Create a test FastAPI app with HTTP routes."""
    config = AppConfig(
        http_routes=[
            HTTPRouteConfig(
                path="/test",
                methods=["GET", "POST"],
                handler=TestHTTPHandler()
            )
        ]
    )
    return create_agent_app(config)


@pytest.fixture
def client(test_app):
    """Create a test client."""
    return TestClient(test_app)


def test_http_get_request(client):
    """Test HTTP GET request."""
    response = client.get("/test")
    assert response.status_code == 200
    data = response.json()
    assert data["test"] == "success"
    assert data["method"] == "GET"


def test_http_post_request(client):
    """Test HTTP POST request."""
    response = client.post("/test", json={"key": "value"})
    assert response.status_code == 200
    data = response.json()
    assert data["test"] == "success"
    assert data["method"] == "POST"


def test_health_endpoint(client):
    """Test the built-in health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "framework" in data


def test_startup_shutdown_hooks():
    """Test that startup and shutdown hooks are called."""
    handler = TestHTTPHandlerWithStartup()
    config = AppConfig(
        http_routes=[
            HTTPRouteConfig(
                path="/test",
                methods=["GET"],
                handler=handler
            )
        ]
    )
    
    app = create_agent_app(config)
    
    with TestClient(app) as client:
        # Test that startup was called
        response = client.get("/test")
        assert response.status_code == 200
        data = response.json()
        assert data["startup_called"] is True
    
    # After context manager exits, shutdown should be called
    assert handler.shutdown_called is True


def test_cors_enabled():
    """Test that CORS is properly configured."""
    config = AppConfig(
        http_routes=[
            HTTPRouteConfig(
                path="/test",
                methods=["GET"],
                handler=TestHTTPHandler()
            )
        ],
        enable_cors=True
    )
    
    app = create_agent_app(config)
    client = TestClient(app)
    
    # Test preflight request
    response = client.options("/test", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_route_config_validation():
    """Test route configuration validation."""
    # Test invalid HTTP method
    with pytest.raises(ValueError):
        HTTPRouteConfig(
            path="/test",
            methods=["INVALID"],
            handler=TestHTTPHandler()
        )
    
    # Test path normalization
    config = HTTPRouteConfig(
        path="test",  # Missing leading slash
        methods=["GET"],
        handler=TestHTTPHandler()
    )
    assert config.path == "/test"