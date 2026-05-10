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

# Global registry for local SocketIO instance (used in Local/Dev mode)
_local_sio = None

def register_local_sio(sio):
    global _local_sio
    _local_sio = sio

class SocketIOLogHandler(logging.Handler):
    """Logging handler that emits logs to SocketIO via Redis or local instance."""
    
    def __init__(self, scan_id=None):
        super().__init__()
        self.scan_id = scan_id
        self.sio = None
        
        # 1. Try Local SIO Registry first (Zero-latency local mode)
        if _local_sio:
            self.sio = _local_sio
            self.mode = "local"
            return

        # 2. Try Redis for distributed mode
        import redis
        try:
            r = redis.from_url(config.redis.url, socket_timeout=1)
            r.ping()
            self.sio = SocketIO(message_queue=config.redis.url)
            self.mode = "distributed"
        except Exception:
            # If everything fails, we'll skip emission in emit()
            self.sio = None
            self.mode = "none"

    def emit(self, record):
        if not self.sio:
            return

        try:
            # Map Python level names to UI level names
            level = record.levelname
            if level == "WARNING":
                level = "WARN"
            elif level == "SUCCESS":
                level = "SUCCESS"
            elif level in ["ERROR", "CRITICAL"]:
                level = "CRITICAL"
            
            payload = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "level": level,
                "msg": record.getMessage(),
                "scan_id": self.scan_id
            }
            
            # Broadcast to all connected clients
            if self.mode == "local":
                # Use direct emit for same-process thread
                self.sio.emit("log_event", payload)
            else:
                # Use Redis-backed emit for distributed mode
                self.sio.emit("log_event", payload)
        except Exception:
            pass # Silently drop logs if emission fails
