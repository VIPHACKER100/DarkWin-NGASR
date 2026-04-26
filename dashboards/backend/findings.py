from flask import Blueprint, jsonify, request
from core.database import SessionLocal
from core.models import Finding

findings_bp = Blueprint("findings", __name__)

@findings_bp.route("/findings", methods=["GET"])
def list_findings():
    scan_id = request.args.get("scan_id")
    db = SessionLocal()
    query = db.query(Finding)
    if scan_id:
        query = query.filter(Finding.scan_id == scan_id)
    
    findings = query.all()
    result = []
    for f in findings:
        result.append({
            "id": f.id,
            "vuln_type": f.vuln_type,
            "severity": f.severity,
            "endpoint": f.endpoint,
            "description": f.description,
            "false_positive": f.false_positive
        })
    db.close()
    return jsonify(result)

@findings_bp.route("/findings/<int:finding_id>/toggle-fp", methods=["POST"])
def toggle_fp(finding_id):
    db = SessionLocal()
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if finding:
        finding.false_positive = not finding.false_positive
        db.commit()
    db.close()
    return jsonify({"status": "success"})
