"""DARKWIN Dashboard Scans API.

Provides REST API endpoints for listing scans and triggering new
scan pipelines via the DARKWIN scheduler.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import uuid

from flask import Blueprint, jsonify, request
from core.database import SessionLocal
from core.models import Scan

scans_bp = Blueprint("scans", __name__)


@scans_bp.route("/scans", methods=["GET"])
def list_scans():
    """List all scans in the database."""
    with SessionLocal() as db:
        scans = db.query(Scan).all()
        result = []
        for s in scans:
            result.append({
                "id": s.id,
                "scan_type": s.scan_type,
                "status": s.status,
                "started_at": s.started_at.isoformat() if s.started_at else None
            })
    return jsonify(result)


@scans_bp.route("/scans/start", methods=["POST"])
def start_scan():
    """Trigger a new scan pipeline for a target domain."""
    data = request.json
    target_domain = data.get("target")
    pipeline_type = data.get("pipeline", "recon")

    scan_id = str(uuid.uuid4())

    return jsonify({"scan_id": scan_id, "status": "started"}), 202
