from flask_socketio import SocketIO, emit

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

def broadcast_scan_update(scan_id, status):
    socketio.emit("scan_update", {"scan_id": scan_id, "status": status})
