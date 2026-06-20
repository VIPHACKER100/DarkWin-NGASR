"""DARKWIN Dashboard Findings API.

Provides REST API endpoints for retrieving and managing scan findings,
including false-positive toggling.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from flask import Blueprint, jsonify, request
from core.database import SessionLocal
from core.models import Finding

findings_bp = Blueprint("findings", __name__)


@findings_bp.route("/findings", methods=["GET"])
def list_findings():
    """List findings, optionally filtered by scan_id."""
    scan_id = request.args.get("scan_id")
    with SessionLocal() as db:
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
    return jsonify(result)


@findings_bp.route("/findings/<int:finding_id>/toggle-fp", methods=["POST"])
def toggle_fp(finding_id: int):
    """Toggle the false_positive flag on a finding."""
    with SessionLocal() as db:
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if finding:
            finding.false_positive = not finding.false_positive
            db.commit()
    return jsonify({"status": "success"})
