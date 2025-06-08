"""
Tests for configuration classes.
"""

import pytest
from agent_api_framework import AppConfig, HTTPRouteConfig, WSRouteConfig, AgentHTTPHandler, AgentWSHandler
from agent_api_framework.config import CORSConfig
from fastapi import Request, WebSocket
from fastapi.responses import JSONResponse


class DummyHTTPHandler(AgentHTTPHandler):
    async def handle(self, request: Request) -> JSONResponse:
        return JSONResponse({"test": "ok"})


class DummyWSHandler(AgentWSHandler):
    async def handle(self, websocket: WebSocket):
        pass


def test_http_route_config():
    """Test HTTPRouteConfig validation and normalization."""
    handler = DummyHTTPHandler()
    
    # Test basic configuration
    config = HTTPRouteConfig(
        path="/api/test",
        methods=["GET", "POST"],
        handler=handler
    )
    assert config.path == "/api/test"
    assert config.methods == ["GET", "POST"]
    assert config.handler == handler
    
    # Test path normalization
    config = HTTPRouteConfig(
        path="api/test",  # Missing leading slash
        methods=["get"],  # Lowercase method
        handler=handler
    )
    assert config.path == "/api/test"
    assert config.methods == ["GET"]
    
    # Test invalid HTTP method
    with pytest.raises(ValueError, match="Invalid HTTP method"):
        HTTPRouteConfig(
            path="/test",
            methods=["INVALID"],
            handler=handler
        )


def test_ws_route_config():
    """Test WSRouteConfig validation and normalization."""
    handler = DummyWSHandler()
    
    # Test basic configuration
    config = WSRouteConfig(
        path="/ws/test",
        handler=handler
    )
    assert config.path == "/ws/test"
    assert config.handler == handler
    assert config.name is None
    
    # Test path normalization
    config = WSRouteConfig(
        path="ws/test",  # Missing leading slash
        handler=handler,
        name="test_ws"
    )
    assert config.path == "/ws/test"
    assert config.name == "test_ws"


def test_cors_config():
    """Test CORSConfig default values and customization."""
    # Test default configuration
    cors = CORSConfig()
    assert cors.allow_origins == ["*"]
    assert cors.allow_credentials is True
    assert cors.allow_methods == ["*"]
    assert cors.allow_headers == ["*"]
    
    # Test custom configuration
    cors = CORSConfig(
        allow_origins=["http://localhost:3000"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"]
    )
    assert cors.allow_origins == ["http://localhost:3000"]
    assert cors.allow_credentials is False
    assert cors.allow_methods == ["GET", "POST"]
    assert cors.allow_headers == ["Content-Type"]


def test_app_config():
    """Test AppConfig validation and defaults."""
    # Test minimal configuration
    config = AppConfig()
    assert config.http_routes == []
    assert config.ws_routes == []
    assert config.host == "0.0.0.0"
    assert config.port == 8000
    assert config.title == "Agent API"
    assert config.enable_cors is True
    assert config.log_level == "info"
    
    # Test custom configuration
    http_handler = DummyHTTPHandler()
    ws_handler = DummyWSHandler()
    
    config = AppConfig(
        http_routes=[
            HTTPRouteConfig(path="/test", methods=["GET"], handler=http_handler)
        ],
        ws_routes=[
            WSRouteConfig(path="/ws/test", handler=ws_handler)
        ],
        host="127.0.0.1",
        port=9000,
        title="Custom API",
        log_level="debug"
    )
    
    assert len(config.http_routes) == 1
    assert len(config.ws_routes) == 1
    assert config.host == "127.0.0.1"
    assert config.port == 9000
    assert config.title == "Custom API"
    assert config.log_level == "debug"


def test_app_config_validation():
    """Test AppConfig validation errors."""
    # Test invalid log level
    with pytest.raises(ValueError, match="Invalid log level"):
        AppConfig(log_level="invalid")
    
    # Test invalid port
    with pytest.raises(ValueError, match="Invalid port number"):
        AppConfig(port=0)
    
    with pytest.raises(ValueError, match="Invalid port number"):
        AppConfig(port=70000)
    
    # Test invalid workers
    with pytest.raises(ValueError, match="Workers must be at least 1"):
        AppConfig(workers=0)