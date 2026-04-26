from flask import Blueprint, jsonify, request
from core.database import SessionLocal
from core.models import Scan, Target, Finding

api_bp = Blueprint("api_v1", __name__)

@api_bp.route("/scans", methods=["GET"])
def list_scans():
    with SessionLocal() as db:
        scans = db.query(Scan).all()
        return jsonify([{
            "id": s.id,
            "target": s.target.domain,
            "status": s.status,
            "started_at": s.started_at
        } for s in scans])

@api_bp.route("/scans/<scan_id>", methods=["GET"])
def get_scan(scan_id):
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return jsonify({"error": "Scan not found"}), 404
        
        findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()
        return jsonify({
            "id": scan.id,
            "status": scan.status,
            "findings": [{
                "type": f.vuln_type,
                "severity": f.severity,
                "endpoint": f.endpoint
            } for f in findings]
        })

@api_bp.route("/scans", methods=["POST"])
def create_scan():
    data = request.json
    target_domain = data.get("target")
    # In a real app, this would trigger a Celery task
    return jsonify({"message": "Scan initiated", "scan_id": "placeholder-id"}), 201
