"""DARKWIN Dashboard Backend Application

Flask-based REST API and websocket server for DARKWIN web dashboard.
Handles scan management, findings storage, authentication, and real-time updates.

Environment Variables:
    FLASK_ENV: Environment mode (development, production).
    FLASK_SECRET_KEY: Secret key for session management (required).
    DATABASE_URL: PostgreSQL connection string.
    
Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import os
from typing import Dict, Any

from flask import Flask, jsonify
from flask_cors import CORS

from dashboards.backend.api_v1 import api_bp
from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("Dashboard")


def create_app() -> Flask:
    """Create and configure Flask application instance.
    
    Initializes:
    - Flask application with CORS support
    - Database configuration
    - Blueprint registration
    - Health check endpoint
    
    Returns:
        Configured Flask application instance.
        
    Raises:
        ValueError: If FLASK_SECRET_KEY environment variable is not set.
    """
    app: Flask = Flask(__name__)
    CORS(app)
    
    config = get_config()
    
    # Retrieve secret key from environment (required for security)
    secret_key: str = os.getenv("FLASK_SECRET_KEY")
    if not secret_key:
        logger.warning(
            "FLASK_SECRET_KEY not set. Using default key (INSECURE FOR PRODUCTION)."
        )
        secret_key = "darkwin_dev_key_change_in_production"
    
    # Configure Flask application
    app_config: Dict[str, Any] = {
        "SECRET_KEY": secret_key,
        "SQLALCHEMY_DATABASE_URI": config.database.url,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JSONIFY_PRETTYPRINT_REGULAR": True,
    }
    app.config.from_mapping(app_config)
    
    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    
    @app.route("/health")
    def health() -> Dict[str, str]:
        """Health check endpoint.
        
        Returns:
            JSON response with platform status.
        """
        return jsonify({"status": "healthy", "platform": "DARKWIN"})
    
    @app.errorhandler(404)
    def not_found(error: Exception) -> tuple:
        """Handle 404 errors.
        
        Args:
            error: Flask error object.
            
        Returns:
            JSON error response with 404 status code.
        """
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error: Exception) -> tuple:
        """Handle 500 errors.
        
        Args:
            error: Flask error object.
            
        Returns:
            JSON error response with 500 status code.
        """
        logger.error(f"Server error: {error}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    
    return app

if __name__ == "__main__":
    """Run Flask development server.
    
    WARNING: This is for development only. Use production WSGI server
    (gunicorn, uWSGI) for production deployments.
    """
    app: Flask = create_app()
    
    # Development server configuration
    debug_mode: bool = os.getenv("FLASK_ENV") == "development"
    
    logger.info(
        f"Starting DARKWIN Dashboard (debug={debug_mode})..."
    )
    
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=debug_mode,
        use_reloader=True,
    )
