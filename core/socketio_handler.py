"""DARKWIN WebSocket Log Emitter

Allows backend processes (scanners, agents) to emit real-time logs
to the web dashboard via Redis and Flask-SocketIO.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import logging
from datetime import datetime
from flask_socketio import SocketIO
from core.config_manager import get_config

config = get_config()

class SocketIOLogHandler(logging.Handler):
    """Logging handler that emits logs to SocketIO via Redis message queue."""
    
    def __init__(self, scan_id=None):
        super().__init__()
        self.scan_id = scan_id
        
        # Test Redis connection before initializing SocketIO to avoid spam
        import redis
        try:
            r = redis.from_url(config.redis.url, socket_timeout=1)
            r.ping()
        except Exception:
            raise ConnectionError("Redis is not reachable")
            
        # Initialize SocketIO in 'client only' mode with message queue
        self.sio = SocketIO(message_queue=config.redis.url)

    def emit(self, record):
        try:
            # Map Python level names to UI level names
            level = record.levelname
            if level == "WARNING":
                level = "WARN"
            elif level == "CRITICAL":
                level = "CRITICAL"
            elif level == "ERROR":
                level = "CRITICAL" # Map error to critical for high visibility
            
            payload = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "level": level,
                "msg": record.getMessage(),
                "scan_id": self.scan_id
            }
            # Broadcast to all connected clients
            self.sio.emit("log_event", payload)
        except Exception:
            self.handleError(record)
