"""
DARKWIN WebSocket Log Emitter

Allows backend processes (scanners, agents) to emit real-time logs
to the web dashboard via Redis and Flask-SocketIO.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: MIT
"""

import logging
from datetime import datetime
from typing import Optional
from flask_socketio import SocketIO
from redis import Redis
from redis.exceptions import RedisError
from core.config_manager import get_config

config = get_config()

_local_sio: Optional[SocketIO] = None


def register_local_sio(sio: SocketIO) -> None:
    """Register a local SocketIO instance for same-process mode."""
    global _local_sio
    _local_sio = sio


class SocketIOLogHandler(logging.Handler):
    """Logging handler that emits logs to SocketIO via Redis or local instance."""

    def __init__(self, scan_id: Optional[str] = None) -> None:
        super().__init__()
        self.scan_id = scan_id
        self.sio: Optional[SocketIO] = None
        self.mode: str = "none"

        if _local_sio:
            self.sio = _local_sio
            self.mode = "local"
            return

        try:
            r = Redis.from_url(config.redis.url, socket_timeout=1)
            r.ping()
            self.sio = SocketIO(message_queue=config.redis.url)
            self.mode = "distributed"
        except RedisError:
            self.sio = None
            self.mode = "none"

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to connected WebSocket clients."""
        if not self.sio:
            return

        try:
            level = record.levelname
            if level == "WARNING":
                level = "WARN"
            elif level in ["ERROR", "CRITICAL"]:
                level = "CRITICAL"

            payload = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "level": level,
                "msg": record.getMessage(),
                "scan_id": self.scan_id
            }

            self.sio.emit("log_event", payload)
        except (OSError, RuntimeError, TypeError):
            pass
