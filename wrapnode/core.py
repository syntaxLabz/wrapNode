"""
Core functionality for creating and configuring the FastAPI application.
"""

import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import AppConfig
from .utils import setup_logging


async def http_route_handler(handler, request: Request):
    """
    Generic HTTP route handler that wraps agent handlers.
    
    Args:
        handler: The agent handler instance
        request: The FastAPI request object
        
    Returns:
        The response from the agent handler
    """
    try:
        return await handler.handle(request)
    except Exception as e:
        logging.error(f"Error in HTTP handler {handler.__class__.__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def ws_route_handler(handler, websocket: WebSocket):
    """
    Generic WebSocket route handler that wraps agent handlers.
    
    Args:
        handler: The agent handler instance
        websocket: The FastAPI WebSocket object
    """
    try:
        # Check if connection should be accepted
        if hasattr(handler, 'on_connect'):
            should_accept = await handler.on_connect(websocket)
            if not should_accept:
                await websocket.close(code=1008, reason="Connection rejected")
                return
        
        await websocket.accept()
        await handler.handle(websocket)
        
    except Exception as e:
        logging.error(f"Error in WebSocket handler {handler.__class__.__name__}: {str(e)}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass  # Connection might already be closed
    finally:
        # Call disconnect hook if available
        if hasattr(handler, 'on_disconnect'):
            try:
                await handler.on_disconnect(websocket, 1000)
            except:
                pass  # Ignore errors in disconnect handler


def create_agent_app(config: AppConfig) -> FastAPI:
    """
    Create a FastAPI application with the given configuration.
    
    Args:
        config: The application configuration
        
    Returns:
        FastAPI: The configured FastAPI application instance
    """
    # Setup logging
    setup_logging(config.log_level)
    
    # Create FastAPI app
    app = FastAPI(
        title=config.title,
        description=config.description,
        version=config.version,
    )
    
    # Add CORS middleware if enabled
    if config.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_config.allow_origins,
            allow_credentials=config.cors_config.allow_credentials,
            allow_methods=config.cors_config.allow_methods,
            allow_headers=config.cors_config.allow_headers,
        )
    
    # Add custom middleware if provided
    if config.middleware:
        for middleware in config.middleware:
            app.add_middleware(middleware)
    
    # Store handlers for lifecycle management
    app.state.http_handlers = []
    app.state.ws_handlers = []
    
    # Register HTTP routes
    for route_config in config.http_routes:
        app.state.http_handlers.append(route_config.handler)
        
        # Create route for each HTTP method
        for method in route_config.methods:
            app.add_api_route(
                path=route_config.path,
                endpoint=lambda req, handler=route_config.handler: http_route_handler(handler, req),
                methods=[method],
                tags=route_config.tags,
                summary=route_config.summary,
                description=route_config.description,
            )
    
    # Register WebSocket routes
    for route_config in config.ws_routes:
        app.state.ws_handlers.append(route_config.handler)
        
        app.add_api_websocket_route(
            path=route_config.path,
            endpoint=lambda ws, handler=route_config.handler: ws_route_handler(handler, ws),
            name=route_config.name,
        )
    
    # Add startup event handler
    @app.on_event("startup")
    async def startup_event():
        """Call startup hooks for all handlers."""
        logging.info("Starting up Agent API Framework...")
        
        # Call startup hooks for HTTP handlers
        for handler in app.state.http_handlers:
            if hasattr(handler, 'on_startup'):
                try:
                    await handler.on_startup()
                except Exception as e:
                    logging.error(f"Error in startup hook for {handler.__class__.__name__}: {str(e)}")
        
        # Call startup hooks for WebSocket handlers
        for handler in app.state.ws_handlers:
            if hasattr(handler, 'on_startup'):
                try:
                    await handler.on_startup()
                except Exception as e:
                    logging.error(f"Error in startup hook for {handler.__class__.__name__}: {str(e)}")
        
        logging.info("Agent API Framework started successfully!")
    
    # Add shutdown event handler
    @app.on_event("shutdown")
    async def shutdown_event():
        """Call shutdown hooks for all handlers."""
        logging.info("Shutting down Agent API Framework...")
        
        # Call shutdown hooks for HTTP handlers
        for handler in app.state.http_handlers:
            if hasattr(handler, 'on_shutdown'):
                try:
                    await handler.on_shutdown()
                except Exception as e:
                    logging.error(f"Error in shutdown hook for {handler.__class__.__name__}: {str(e)}")
        
        # Call shutdown hooks for WebSocket handlers
        for handler in app.state.ws_handlers:
            if hasattr(handler, 'on_shutdown'):
                try:
                    await handler.on_shutdown()
                except Exception as e:
                    logging.error(f"Error in shutdown hook for {handler.__class__.__name__}: {str(e)}")
        
        logging.info("Agent API Framework shut down successfully!")
    
    # Add health check endpoint
    @app.get("/health", tags=["system"])
    async def health_check():
        """Health check endpoint."""
        return JSONResponse({
            "status": "healthy",
            "framework": "Agent API Framework",
            "version": config.version
        })
    
    return app