"""DARKWIN Dashboard WebSocket Manager.

Manages SocketIO connections for real-time scan status updates
and live log streaming to the DARKWIN web dashboard.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from flask_socketio import SocketIO, emit

socketio = SocketIO(cors_allowed_origins="*")


@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


def broadcast_scan_update(scan_id: str, status: str) -> None:
    """Broadcast a scan status update to all connected dashboard clients.

    Args:
        scan_id: Unique scan identifier.
        status: Current scan status (running, completed, failed).
    """
    socketio.emit("scan_update", {"scan_id": scan_id, "status": status})
