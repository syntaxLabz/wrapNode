"""
Example multi-agent application using the Agent API Framework.
"""

from agent_api_framework import AppConfig, HTTPRouteConfig, WSRouteConfig, create_agent_app
from echo_http import EchoHandler
from health_http import HealthHandler
from echo_ws import EchoWSHandler
from chat_ws import ChatWSHandler

# Create application configuration
app_config = AppConfig(
    title="Multi-Agent API Example",
    description="Example application showcasing multiple HTTP and WebSocket agents",
    version="1.0.0",
    http_routes=[
        HTTPRouteConfig(
            path="/api/echo", 
            methods=["POST", "GET"], 
            handler=EchoHandler(),
            tags=["utilities"],
            summary="Echo endpoint",
            description="Echoes back the request data with additional metadata"
        ),
        HTTPRouteConfig(
            path="/api/health", 
            methods=["GET"], 
            handler=HealthHandler(),
            tags=["system"],
            summary="Health check",
            description="Returns detailed health status and system metrics"
        ),
    ],
    ws_routes=[
        WSRouteConfig(
            path="/ws/echo", 
            handler=EchoWSHandler(),
            name="echo_websocket"
        ),
        WSRouteConfig(
            path="/ws/chat", 
            handler=ChatWSHandler(),
            name="chat_websocket"
        ),
    ],
    host="0.0.0.0",
    port=9000,
    log_level="info",
    enable_cors=True,
)

# Create the FastAPI app
app = create_agent_app(app_config)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Multi-Agent API Server...")
    print("📖 API Documentation: http://localhost:9000/docs")
    print("🔗 WebSocket Echo: ws://localhost:9000/ws/echo")
    print("💬 WebSocket Chat: ws://localhost:9000/ws/chat")
    
    uvicorn.run(
        app, 
        host=app_config.host, 
        port=app_config.port,
        log_level=app_config.log_level
    )