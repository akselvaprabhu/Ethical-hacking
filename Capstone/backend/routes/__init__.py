from routes.auth_routes import auth_bp
from routes.api_routes import api_bp
from routes.security_routes import security_bp

__all__ = ['auth_bp', 'api_bp', 'security_bp']
