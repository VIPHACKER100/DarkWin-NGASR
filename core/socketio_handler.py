"""DARKWIN WebSocket Log Emitter

Allows backend processes (scanners, agents) to emit real-time logs
to the web dashboard via Redis and Flask-SocketIO.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import logging
from flask_socketio import SocketIO
from core.config_manager import get_config

config = get_config()

class SocketIOLogHandler(logging.Handler):
    """Logging handler that emits logs to SocketIO via Redis message queue."""
    
    def __init__(self, scan_id=None):
        super().__init__()
        self.scan_id = scan_id
        # Initialize SocketIO in 'client only' mode with message queue
        self.sio = SocketIO(message_queue=config.redis.url)

    def emit(self, record):
        try:
            log_entry = self.format(record)
            payload = {
                "time": datetime.utcnow().strftime("%H:%M:%S"),
                "level": record.levelname,
                "msg": record.getMessage(),
                "scan_id": self.scan_id
            }
            # Broadcast to all connected clients
            self.sio.emit("log_event", payload, namespace="/")
        except Exception:
            self.handleError(record)

from datetime import datetime
