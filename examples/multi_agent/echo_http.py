from agent_api_framework import AgentHTTPHandler
from fastapi import Request
from fastapi.responses import JSONResponse


class EchoHandler(AgentHTTPHandler):
    """
    Simple echo handler that returns the request data back to the client.
    """
    
    async def handle(self, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except:
            body = {"message": "No JSON body provided"}
        
        return JSONResponse({
            "echo": body,
            "method": request.method,
            "path": str(request.url.path),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params)
        })
    
    async def on_startup(self):
        print("EchoHandler started up!")
    
    async def on_shutdown(self):
        print("EchoHandler shutting down!")