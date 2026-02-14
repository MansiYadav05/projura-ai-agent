"""
CORS (Cross-Origin Resource Sharing) Handler
Implements CORS validation and headers for the Flask application
"""

from flask import request, jsonify
from functools import wraps
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Allowed origins - configure based on your environment
ALLOWED_ORIGINS = [
    "http://localhost:5000",
    "http://localhost:3000",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:3000",
    os.getenv('FRONTEND_URL', 'http://localhost:5000'),  # From environment
]

# If in production, add your domain
if os.getenv('ENVIRONMENT') == 'production':
    ALLOWED_ORIGINS.extend([
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ])


def validate_origin(origin: Optional[str]) -> bool:
    """
    Validate if the request origin is allowed
    
    Args:
        origin: The origin from the request header
        
    Returns:
        bool: True if origin is allowed, False otherwise
    """
    if not origin:
        return False
    
    # Check exact match
    if origin in ALLOWED_ORIGINS:
        return True
    
    # Development: Allow requests without origin header
    if os.getenv('ENVIRONMENT') == 'development':
        return True
    
    return False


def add_cors_headers(response, origin: Optional[str] = None):
    """
    Add CORS headers to response
    
    Args:
        response: Flask response object
        origin: The origin to allow (if valid)
    """
    request_origin = origin or request.headers.get('Origin')
    
    if validate_origin(request_origin):
        # origin-when-cross-origin: Include origin in response for cross-origin requests
        response.headers['Access-Control-Allow-Origin'] = request_origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    else:
        # For same-origin or invalid origins, use a safe default
        response.headers['Access-Control-Allow-Origin'] = request_origin or '*'
    
    # Allowed HTTP methods
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
    
    # Allowed headers in requests
    response.headers['Access-Control-Allow-Headers'] = (
        'Content-Type, Authorization, X-Requested-With, '
        'X-CSRF-Token, Accept, Origin'
    )
    
    # How long preflight response can be cached (in seconds)
    response.headers['Access-Control-Max-Age'] = '3600'  # 1 hour
    
    # Whether credentials (cookies, authorization headers) are allowed
    response.headers['Access-Control-Expose-Headers'] = (
        'Content-Type, Authorization, X-Total-Count'
    )
    
    return response


def cors_required(f):
    """
    Decorator to add CORS headers to all responses
    Apply this to routes that need CORS support
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Handle preflight OPTIONS requests
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.status_code = 200
            return add_cors_headers(response)
        
        # Execute the route function
        result = f(*args, **kwargs)
        
        # Handle different return types
        if isinstance(result, tuple):
            response, status_code = result[0], result[1] if len(result) > 1 else 200
        else:
            response = result
            status_code = 200
        
        # Add CORS headers
        if hasattr(response, 'headers'):
            response = add_cors_headers(response)
        
        if isinstance(result, tuple):
            return response, status_code
        return response
    
    return decorated_function


def cors_error_handler(error_code: int):
    """
    Create a CORS-enabled error response
    
    Args:
        error_code: HTTP error code
        
    Returns:
        tuple: (response, status_code)
    """
    def error_response(message: str):
        response = jsonify({
            'error': message,
            'status_code': error_code
        })
        response.status_code = error_code
        return add_cors_headers(response)
    
    return error_response
