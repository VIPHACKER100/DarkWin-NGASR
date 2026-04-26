from flask import Blueprint, jsonify, request
from core.database import SessionLocal
from core.models import Scan
import uuid

scans_bp = Blueprint("scans", __name__)

@scans_bp.route("/scans", methods=["GET"])
def list_scans():
    db = SessionLocal()
    scans = db.query(Scan).all()
    result = []
    for s in scans:
        result.append({
            "id": s.id,
            "scan_type": s.scan_type,
            "status": s.status,
            "started_at": s.started_at.isoformat() if s.started_at else None
        })
    db.close()
    return jsonify(result)

@scans_bp.route("/scans/start", methods=["POST"])
def start_scan():
    data = request.json
    target_domain = data.get("target")
    pipeline_type = data.get("pipeline", "recon")
    
    scan_id = str(uuid.uuid4())
    # In a real implementation, this would trigger a Celery task
    # from core.scheduler import run_module_task
    # run_module_task.delay(...)
    
    return jsonify({"scan_id": scan_id, "status": "started"}), 202
