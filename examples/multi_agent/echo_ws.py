from agent_api_framework import AgentWSHandler
from fastapi import WebSocket
import json
import time


class EchoWSHandler(AgentWSHandler):
    """
    Simple WebSocket echo handler that echoes back received messages.
    """
    
    async def handle(self, websocket: WebSocket):
        try:
            # Send welcome message
            await websocket.send_text(json.dumps({
                "type": "system",
                "message": "Echo WebSocket connected! Send me any message and I'll echo it back.",
                "timestamp": time.time()
            }))
            
            while True:
                message = await websocket.receive_text()
                
                # Try to parse as JSON, fallback to plain text
                try:
                    data = json.loads(message)
                    response = {
                        "type": "echo",
                        "original": data,
                        "timestamp": time.time()
                    }
                except json.JSONDecodeError:
                    response = {
                        "type": "echo",
                        "original": message,
                        "timestamp": time.time()
                    }
                
                await websocket.send_text(json.dumps(response))
                
        except Exception as e:
            print(f"Echo WebSocket error: {e}")
    
    async def on_connect(self, websocket: WebSocket) -> bool:
        print("Echo WebSocket connection requested")
        return True
    
    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        print(f"Echo WebSocket disconnected with code: {close_code}")