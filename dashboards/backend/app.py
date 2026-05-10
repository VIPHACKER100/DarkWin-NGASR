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


from flask_socketio import SocketIO, emit

def create_app() -> tuple[Flask, SocketIO]:
    """Create and configure Flask application and SocketIO instance."""
    app: Flask = Flask(__name__)
    CORS(app)
    
    # Initialize SocketIO with optional Redis message queue
    config = get_config()
    try:
        import redis
        r = redis.from_url(config.redis.url, socket_timeout=1)
        r.ping()
        socketio = SocketIO(app, cors_allowed_origins="*", message_queue=config.redis.url)
        logger.info("SocketIO initialized with Redis message queue.")
    except Exception:
        socketio = SocketIO(app, cors_allowed_origins="*")
        logger.warning("Redis unreachable. SocketIO initialized without message queue (Local mode).")
    
    # Retrieve secret key from environment
    secret_key: str = os.getenv("FLASK_SECRET_KEY")
    if not secret_key:
        secret_key = "darkwin_dev_key_change_in_production"
    
    app.config.from_mapping({
        "SECRET_KEY": secret_key,
        "SQLALCHEMY_DATABASE_URI": config.database.url,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    
    @app.route("/health")
    def health():
        """Consolidated health check for external monitoring."""
        status = {
            "status": "healthy",
            "services": {
                "database": "ok",
                "redis": "ok",
                "websocket": "enabled"
            }
        }
        
        # 1. Database Check
        try:
            from core.database import get_engine
            from sqlalchemy import text
            with get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            status["services"]["database"] = "fail"
            status["status"] = "degraded"

        # 2. Redis Check
        try:
            from core.cache_manager import global_cache
            if not global_cache.redis or not global_cache.redis.ping():
                status["services"]["redis"] = "fail"
                status["status"] = "degraded"
        except Exception:
            status["services"]["redis"] = "error"
            status["status"] = "degraded"

        return jsonify(status), 200 if status["status"] == "healthy" else 500
    
    @socketio.on("connect")
    def handle_connect():
        logger.info("Websocket client connected")
        emit("status", {"msg": "Connected to DARKWIN Mesh"})

    return app, socketio

if __name__ == "__main__":
    app, socketio = create_app()
    debug_mode = os.getenv("FLASK_ENV") == "development"
    port = int(os.getenv("FLASK_PORT", "5000"))
    
    logger.info(f"Starting DARKWIN Dashboard with WebSocket support on port {port}...")
    socketio.run(app, host="0.0.0.0", port=port, debug=debug_mode, allow_unsafe_werkzeug=True)
