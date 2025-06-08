"""
Command-line interface for the Agent API Framework.
"""

import typer
import uvicorn
import importlib.util
import sys
from pathlib import Path
from typing import List, Optional
from .config import AppConfig, HTTPRouteConfig, WSRouteConfig
from .core import create_agent_app

app = typer.Typer(help="Agent API Framework CLI")


def load_handler_from_module(module_path: str, handler_class: str):
    """
    Load a handler class from a Python module.
    
    Args:
        module_path: Path to the Python module
        handler_class: Name of the handler class
        
    Returns:
        The handler class
    """
    spec = importlib.util.spec_from_file_location("handler_module", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["handler_module"] = module
    spec.loader.exec_module(module)
    
    return getattr(module, handler_class)


@app.command()
def run(
    agent_dir: str = typer.Option("./agents", help="Directory containing agent handlers"),
    port: int = typer.Option(8000, help="Port to run the server on"),
    host: str = typer.Option("0.0.0.0", help="Host to bind the server to"),
    http: Optional[List[str]] = typer.Option(None, help="HTTP routes in format /path:HandlerClass"),
    ws: Optional[List[str]] = typer.Option(None, help="WebSocket routes in format /path:HandlerClass"),
    log_level: str = typer.Option("info", help="Log level"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
    workers: int = typer.Option(1, help="Number of worker processes"),
):
    """
    Run the Agent API server with the specified configuration.
    """
    agent_path = Path(agent_dir)
    if not agent_path.exists():
        typer.echo(f"Error: Agent directory '{agent_dir}' does not exist", err=True)
        raise typer.Exit(1)
    
    # Parse HTTP routes
    http_routes = []
    if http:
        for route_spec in http:
            try:
                path, handler_class = route_spec.split(":")
                handler_module = agent_path / f"{handler_class.lower()}.py"
                
                if not handler_module.exists():
                    typer.echo(f"Error: Handler module '{handler_module}' not found", err=True)
                    raise typer.Exit(1)
                
                HandlerClass = load_handler_from_module(str(handler_module), handler_class)
                handler_instance = HandlerClass()
                
                http_routes.append(HTTPRouteConfig(
                    path=path,
                    methods=["GET", "POST"],  # Default methods
                    handler=handler_instance
                ))
            except ValueError:
                typer.echo(f"Error: Invalid HTTP route format '{route_spec}'. Use /path:HandlerClass", err=True)
                raise typer.Exit(1)
    
    # Parse WebSocket routes
    ws_routes = []
    if ws:
        for route_spec in ws:
            try:
                path, handler_class = route_spec.split(":")
                handler_module = agent_path / f"{handler_class.lower()}.py"
                
                if not handler_module.exists():
                    typer.echo(f"Error: Handler module '{handler_module}' not found", err=True)
                    raise typer.Exit(1)
                
                HandlerClass = load_handler_from_module(str(handler_module), handler_class)
                handler_instance = HandlerClass()
                
                ws_routes.append(WSRouteConfig(
                    path=path,
                    handler=handler_instance
                ))
            except ValueError:
                typer.echo(f"Error: Invalid WebSocket route format '{route_spec}'. Use /path:HandlerClass", err=True)
                raise typer.Exit(1)
    
    # Create app configuration
    config = AppConfig(
        http_routes=http_routes,
        ws_routes=ws_routes,
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
        workers=workers,
    )
    
    # Create and run the app
    fastapi_app = create_agent_app(config)
    
    typer.echo(f"Starting Agent API server on {host}:{port}")
    typer.echo(f"HTTP routes: {len(http_routes)}")
    typer.echo(f"WebSocket routes: {len(ws_routes)}")
    
    uvicorn.run(
        fastapi_app,
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
        workers=workers if not reload else 1,
    )


@app.command()
def init(
    directory: str = typer.Option("./my_agents", help="Directory to create agent template"),
):
    """
    Initialize a new agent project with example handlers.
    """
    project_path = Path(directory)
    project_path.mkdir(exist_ok=True)
    
    # Create example handlers
    examples = {
        "echo_http.py": '''from agent_api_framework import AgentHTTPHandler
from fastapi import Request
from fastapi.responses import JSONResponse

class EchoHandler(AgentHTTPHandler):
    async def handle(self, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except:
            body = {"message": "No JSON body provided"}
        
        return JSONResponse({
            "echo": body,
            "method": request.method,
            "path": str(request.url.path)
        })
''',
        "health_http.py": '''from agent_api_framework import AgentHTTPHandler
from fastapi import Request
from fastapi.responses import JSONResponse
import time

class HealthHandler(AgentHTTPHandler):
    def __init__(self):
        self.start_time = time.time()
    
    async def handle(self, request: Request) -> JSONResponse:
        uptime = time.time() - self.start_time
        return JSONResponse({
            "status": "healthy",
            "uptime_seconds": round(uptime, 2),
            "timestamp": time.time()
        })
''',
        "echo_ws.py": '''from agent_api_framework import AgentWSHandler
from fastapi import WebSocket

class EchoWSHandler(AgentWSHandler):
    async def handle(self, websocket: WebSocket):
        try:
            while True:
                message = await websocket.receive_text()
                await websocket.send_text(f"ECHO: {message}")
        except Exception as e:
            print(f"WebSocket error: {e}")
''',
        "chat_ws.py": '''from agent_api_framework import AgentWSHandler
from fastapi import WebSocket
import json
import time

class ChatWSHandler(AgentWSHandler):
    async def handle(self, websocket: WebSocket):
        await websocket.send_text(json.dumps({
            "type": "system",
            "message": "Welcome to the AI chat! Send me a message.",
            "timestamp": time.time()
        }))
        
        try:
            while True:
                message = await websocket.receive_text()
                
                try:
                    data = json.loads(message)
                    user_message = data.get("message", message)
                except:
                    user_message = message
                
                # Simulate AI response
                response = {
                    "type": "agent",
                    "message": f"I received your message: '{user_message}'. This is a simulated AI response!",
                    "timestamp": time.time()
                }
                
                await websocket.send_text(json.dumps(response))
        except Exception as e:
            print(f"Chat WebSocket error: {e}")
''',
        "main.py": '''from agent_api_framework import AppConfig, HTTPRouteConfig, WSRouteConfig, create_agent_app
from echo_http import EchoHandler
from health_http import HealthHandler
from echo_ws import EchoWSHandler
from chat_ws import ChatWSHandler

# Create application configuration
app_config = AppConfig(
    title="My Agent API",
    description="Example agent API using the Agent API Framework",
    http_routes=[
        HTTPRouteConfig(
            path="/echo", 
            methods=["POST"], 
            handler=EchoHandler(),
            summary="Echo endpoint",
            description="Echoes back the request data"
        ),
        HTTPRouteConfig(
            path="/health", 
            methods=["GET"], 
            handler=HealthHandler(),
            summary="Health check",
            description="Returns the health status of the service"
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
    port=9000,
    log_level="info"
)

# Create the FastAPI app
app = create_agent_app(app_config)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
'''
    }
    
    # Write example files
    for filename, content in examples.items():
        file_path = project_path / filename
        file_path.write_text(content)
    
    typer.echo(f"✅ Created agent project in '{directory}'")
    typer.echo("📁 Files created:")
    for filename in examples.keys():
        typer.echo(f"   - {filename}")
    
    typer.echo(f"\n🚀 To run your agents:")
    typer.echo(f"   cd {directory}")
    typer.echo(f"   python main.py")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()