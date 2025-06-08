"""
Utility functions for the Agent API Framework.
"""

import logging
import sys
from typing import Dict, Any


def setup_logging(log_level: str = "info") -> None:
    """
    Setup logging configuration.
    
    Args:
        log_level: The logging level to use
    """
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    
    level = level_map.get(log_level.lower(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set uvicorn log level
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)


def create_error_response(message: str, status_code: int = 500, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        message: The error message
        status_code: HTTP status code
        details: Optional additional details
        
    Returns:
        Dict containing the error response
    """
    response = {
        "error": True,
        "message": message,
        "status_code": status_code,
    }
    
    if details:
        response["details"] = details
    
    return response


def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: The response data
        message: Success message
        
    Returns:
        Dict containing the success response
    """
    response = {
        "success": True,
        "message": message,
    }
    
    if data is not None:
        response["data"] = data
    
    return response