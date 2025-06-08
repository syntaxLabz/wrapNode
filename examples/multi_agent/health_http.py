from agent_api_framework import AgentHTTPHandler
from fastapi import Request
from fastapi.responses import JSONResponse
import time
import psutil
import os


class HealthHandler(AgentHTTPHandler):
    """
    Health check handler that provides system status information.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
    
    async def handle(self, request: Request) -> JSONResponse:
        self.request_count += 1
        uptime = time.time() - self.start_time
        
        # Get system metrics
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
        except:
            cpu_percent = 0
            memory = None
            disk = None
        
        health_data = {
            "status": "healthy",
            "uptime_seconds": round(uptime, 2),
            "timestamp": time.time(),
            "request_count": self.request_count,
            "process_id": os.getpid(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent if memory else None,
                "disk_percent": (disk.used / disk.total * 100) if disk else None,
            }
        }
        
        return JSONResponse(health_data)