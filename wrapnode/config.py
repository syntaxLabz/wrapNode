"""
Configuration classes for the Agent API Framework.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
from .base_http import AgentHTTPHandler
from .base_ws import AgentWSHandler


@dataclass
class HTTPRouteConfig:
    """
    Configuration for an HTTP route.
    
    Attributes:
        path: The URL path for the route (e.g., "/api/echo")
        methods: List of HTTP methods this route accepts (e.g., ["GET", "POST"])
        handler: Instance of AgentHTTPHandler to handle requests
        tags: Optional list of tags for OpenAPI documentation
        summary: Optional summary for OpenAPI documentation
        description: Optional description for OpenAPI documentation
    """
    path: str
    methods: List[str]
    handler: AgentHTTPHandler
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate the configuration after initialization."""
        if not self.path.startswith("/"):
            self.path = "/" + self.path
        
        # Normalize HTTP methods to uppercase
        self.methods = [method.upper() for method in self.methods]
        
        # Validate HTTP methods
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        for method in self.methods:
            if method not in valid_methods:
                raise ValueError(f"Invalid HTTP method: {method}")


@dataclass
class WSRouteConfig:
    """
    Configuration for a WebSocket route.
    
    Attributes:
        path: The URL path for the WebSocket endpoint (e.g., "/ws/chat")
        handler: Instance of AgentWSHandler to handle connections
        name: Optional name for the route
    """
    path: str
    handler: AgentWSHandler
    name: Optional[str] = None
    
    def __post_init__(self):
        """Validate the configuration after initialization."""
        if not self.path.startswith("/"):
            self.path = "/" + self.path


@dataclass
class CORSConfig:
    """
    Configuration for CORS (Cross-Origin Resource Sharing).
    
    Attributes:
        allow_origins: List of allowed origins, or ["*"] for all
        allow_credentials: Whether to allow credentials in CORS requests
        allow_methods: List of allowed HTTP methods
        allow_headers: List of allowed headers
    """
    allow_origins: List[str] = field(default_factory=lambda: ["*"])
    allow_credentials: bool = True
    allow_methods: List[str] = field(default_factory=lambda: ["*"])
    allow_headers: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class AppConfig:
    """
    Main configuration for the Agent API application.
    
    Attributes:
        http_routes: List of HTTP route configurations
        ws_routes: List of WebSocket route configurations
        host: Host address to bind the server to
        port: Port number to bind the server to
        title: Title for the API documentation
        description: Description for the API documentation
        version: Version of the API
        enable_cors: Whether to enable CORS
        cors_config: CORS configuration settings
        middleware: Optional list of middleware functions
        log_level: Logging level (debug, info, warning, error, critical)
        reload: Whether to enable auto-reload in development
        workers: Number of worker processes (for production)
    """
    http_routes: List[HTTPRouteConfig] = field(default_factory=list)
    ws_routes: List[WSRouteConfig] = field(default_factory=list)
    host: str = "0.0.0.0"
    port: int = 8000
    title: str = "Agent API"
    description: str = "AI Agent API powered by FastAPI"
    version: str = "1.0.0"
    enable_cors: bool = True
    cors_config: CORSConfig = field(default_factory=CORSConfig)
    middleware: Optional[List[Callable]] = None
    log_level: str = "info"
    reload: bool = False
    workers: int = 1
    
    def __post_init__(self):
        """Validate the configuration after initialization."""
        # Validate log level
        valid_log_levels = {"debug", "info", "warning", "error", "critical"}
        if self.log_level.lower() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.log_level}")
        
        # Validate port
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid port number: {self.port}")
        
        # Validate workers
        if self.workers < 1:
            raise ValueError(f"Workers must be at least 1, got: {self.workers}")