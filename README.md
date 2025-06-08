# wrapNode

A production-ready Python framework for exposing AI and automation agents via FastAPI endpoints. Build scalable agent APIs with support for both HTTP and WebSocket endpoints, complete with lifecycle management, configuration, and testing utilities.

## 🚀 Features

- **Multiple Endpoint Types**: Support for both HTTP and WebSocket endpoints
- **Independent Handlers**: Each route has its own handler class with lifecycle hooks
- **Full Configuration**: Comprehensive configuration for ports, hosts, CORS, middleware, and logging
- **CLI Tool**: Optional command-line interface for running servers
- **Production Ready**: Built on FastAPI with proper error handling and logging
- **Testing Suite**: Complete unit and integration test coverage
- **Type Safety**: Full type hints and Pydantic validation

## 📦 Installation

```bash
pip install wrapNode
```

For development:
```bash
pip install wrapNode
```

## 🏃 Quick Start

### 1. Create Your First Agent

```python
# echo_agent.py
from wrapNode import AgentHTTPHandler
from fastapi import Request
from fastapi.responses import JSONResponse

class EchoAgent(AgentHTTPHandler):
    async def handle(self, request: Request) -> JSONResponse:
        body = await request.json()
        return JSONResponse({"echo": body, "agent": "EchoAgent"})
```

### 2. Create a WebSocket Agent

```python
# chat_agent.py
from wrapNode import AgentWSHandler
from fastapi import WebSocket
import json

class ChatAgent(AgentWSHandler):
    async def handle(self, websocket: WebSocket):
        await websocket.send_text("Hello! I'm your AI assistant.")
        
        while True:
            message = await websocket.receive_text()
            response = f"AI: I received '{message}'. How can I help?"
            await websocket.send_text(response)
```

### 3. Configure and Run Your API

```python
# main.py
from wrapNode import AppConfig, HTTPRouteConfig, WSRouteConfig, create_agent_app
from echo_agent import EchoAgent
from chat_agent import ChatAgent

# Configure your API
config = AppConfig(
    title="My Agent API",
    description="AI agents powered by Agent API Framework",
    http_routes=[
        HTTPRouteConfig(
            path="/api/echo",
            methods=["POST"],
            handler=EchoAgent(),
            summary="Echo agent endpoint"
        )
    ],
    ws_routes=[
        WSRouteConfig(
            path="/ws/chat",
            handler=ChatAgent(),
            name="chat_agent"
        )
    ],
    port=8000
)

# Create and run the app
app = create_agent_app(config)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. Test Your API

```bash
# Start the server
python main.py

# Test HTTP endpoint
curl -X POST http://localhost:8000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, Agent!"}'

# Test WebSocket (using wscat or similar)
wscat -c ws://localhost:8000/ws/chat
```

## 🏗️ Architecture

### Handler Base Classes

#### HTTP Handlers
```python
from wrapNode import AgentHTTPHandler
from fastapi import Request
from fastapi.responses import JSONResponse

class MyHTTPAgent(AgentHTTPHandler):
    async def handle(self, request: Request) -> JSONResponse:
        # Your agent logic here
        return JSONResponse({"status": "success"})
    
    async def on_startup(self):
        # Optional: Called when the handler starts
        print("HTTP Agent starting up...")
    
    async def on_shutdown(self):
        # Optional: Called when the handler shuts down
        print("HTTP Agent shutting down...")
```

#### WebSocket Handlers
```python
from wrapNode import AgentWSHandler
from fastapi import WebSocket

class MyWSAgent(AgentWSHandler):
    async def handle(self, websocket: WebSocket):
        # Your WebSocket agent logic here
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Processed: {message}")
    
    async def on_connect(self, websocket: WebSocket) -> bool:
        # Optional: Validate connection before accepting
        return True  # Return False to reject
    
    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        # Optional: Handle disconnection
        print(f"Client disconnected with code: {close_code}")
```

### Configuration

```python
from wrapNode import AppConfig, HTTPRouteConfig, WSRouteConfig, CORSConfig

config = AppConfig(
    title="My Agent API",
    description="Production agent API",
    version="1.0.0",
    
    # Routes
    http_routes=[
        HTTPRouteConfig(
            path="/api/agent",
            methods=["GET", "POST"],
            handler=MyAgent(),
            tags=["agents"],
            summary="Main agent endpoint"
        )
    ],
    ws_routes=[
        WSRouteConfig(
            path="/ws/agent",
            handler=MyWSAgent(),
            name="main_agent_ws"
        )
    ],
    
    # Server settings
    host="0.0.0.0",
    port=8000,
    log_level="info",
    
    # CORS configuration
    enable_cors=True,
    cors_config=CORSConfig(
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"]
    )
)
```

## 🛠️ CLI Tool

The framework includes a CLI tool for quick development and deployment:

### Initialize a New Project
```bash
wrapNode init --directory ./my_agents
```

### Run Agents from Command Line
```bash
wrapNode run \
  --agent-dir ./my_agents \
  --port 8080 \
  --http /echo:EchoHandler,/health:HealthHandler \
  --ws /ws/echo:EchoWSHandler,/ws/chat:ChatWSHandler
```

## 🧪 Testing

The framework includes comprehensive testing utilities:

```python
# test_my_agent.py
import pytest
from fastapi.testclient import TestClient
from wrapNode import AppConfig, HTTPRouteConfig, create_agent_app
from my_agent import MyAgent

@pytest.fixture
def test_app():
    config = AppConfig(
        http_routes=[
            HTTPRouteConfig(path="/test", methods=["POST"], handler=MyAgent())
        ]
    )
    return create_agent_app(config)

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

def test_my_agent(client):
    response = client.post("/test", json={"input": "test"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

### WebSocket Testing
```python
def test_websocket_agent(client):
    with client.websocket_connect("/ws/test") as websocket:
        websocket.send_text("Hello")
        data = websocket.receive_text()
        assert "Hello" in data
```

## 📚 Examples

Check out the `examples/` directory for complete working examples:

- **Multi-Agent Setup**: Multiple HTTP and WebSocket agents
- **Production Configuration**: Advanced configuration with middleware
- **Testing Examples**: Comprehensive test suites
- **CLI Usage**: Command-line deployment examples

## 🔧 Advanced Features

### Custom Middleware
```python
from fastapi import Request
import time

async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

config = AppConfig(
    middleware=[timing_middleware],
    # ... other config
)
```

### Error Handling
```python
from wrapNode.utils import create_error_response, create_success_response

class SafeAgent(AgentHTTPHandler):
    async def handle(self, request: Request) -> JSONResponse:
        try:
            # Your agent logic
            result = await self.process_request(request)
            return JSONResponse(create_success_response(result))
        except Exception as e:
            return JSONResponse(
                create_error_response(str(e), status_code=500),
                status_code=500
            )
```

### Logging Configuration
```python
import logging

config = AppConfig(
    log_level="debug",  # debug, info, warning, error, critical
    # ... other config
)

# In your handlers
class LoggingAgent(AgentHTTPHandler):
    async def handle(self, request: Request) -> JSONResponse:
        logging.info(f"Processing request: {request.method} {request.url}")
        # ... your logic
```

## 🚀 Production Deployment

### Using Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📖 API Documentation

When you run your agent API, automatic documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/agent-api-framework/agent-api-framework.git
cd agent-api-framework
pip install -e .[dev]
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://agent-api-framework.readthedocs.io](https://agent-api-framework.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/agent-api-framework/agent-api-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/agent-api-framework/agent-api-framework/discussions)

## 🎯 Roadmap

- [ ] Plugin system for common agent patterns
- [ ] Built-in authentication and authorization
- [ ] Metrics and monitoring integration
- [ ] Agent marketplace and discovery
- [ ] GraphQL support
- [ ] gRPC support
- [ ] Kubernetes operator

---

**Built with ❤️ for the AI agent community**