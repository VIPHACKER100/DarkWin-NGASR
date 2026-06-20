"""DARKWIN Dashboard REST API v1.

Provides REST API endpoints for managing scans, targets, findings,
reports, and real-time mesh status for the DARKWIN web dashboard.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import os
import uuid
import threading
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file, send_from_directory
from core.database import SessionLocal
from core.models import Scan, Target, Finding, Report
from core.reporting_engine import ReportingEngine

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
    from core.scheduler import run_pipeline_task
    from core.cache_manager import global_cache

    data = request.json
    target = data.get("target")
    pipeline = data.get("pipeline", "recon")

    if not target:
        return jsonify({"error": "Target is required"}), 400

    try:
        if global_cache.redis:
            run_pipeline_task.delay(target, pipeline)
            mode = "distributed"
        else:
            thread = threading.Thread(target=run_pipeline_task, args=(target, pipeline))
            thread.daemon = True
            thread.start()
            mode = "local"

        return jsonify({
            "message": f"Pipeline {pipeline} initiated for {target} ({mode} mode)",
            "scan_id": str(uuid.uuid4()),
            "status": "queued",
            "mode": mode
        }), 201

    except (ValueError, OSError, RuntimeError) as e:
        from core.logging_system import get_logger
        logger = get_logger("API")
        logger.error(f"Failed to initiate background scan: {e}")
        return jsonify({"error": f"Failed to launch scan: {str(e)}"}), 500


@api_bp.route("/graph", methods=["GET"])
def get_attack_surface_graph():
    """Returns nodes and edges for 3D attack surface visualization."""
    with SessionLocal() as db:
        targets = db.query(Target).all()
        nodes = []
        edges = []

        nodes.append({"id": "darkwin-root", "label": "DARKWIN Mesh", "type": "root"})

        for t in targets:
            nodes.append({
                "id": f"target-{t.id}",
                "label": t.domain,
                "type": "target"
            })
            edges.append({"source": "darkwin-root", "target": f"target-{t.id}"})

            for s in t.scans:
                for f in s.findings:
                    finding_id = f"finding-{f.id}"
                    nodes.append({
                        "id": finding_id,
                        "label": f.vuln_type,
                        "type": "finding",
                        "severity": f.severity
                    })
                    edges.append({"source": f"target-{t.id}", "target": finding_id})

        return jsonify({"nodes": nodes, "edges": edges})


@api_bp.route("/mesh", methods=["GET"])
def get_mesh_status():
    from core.mesh_manager import MeshManager
    manager = MeshManager()
    return jsonify(manager.list_nodes())


@api_bp.route("/stats", methods=["GET"])
def get_dashboard_stats():
    """Returns aggregated statistics for the overview dashboard."""
    with SessionLocal() as db:
        total_targets = db.query(Target).count()
        total_findings = db.query(Finding).count()
        critical_findings = db.query(Finding).filter(Finding.severity == "Critical").count()
        active_scans = db.query(Scan).filter(Scan.status == "running").count()

        recent_findings = db.query(Finding).order_by(Finding.id.desc()).limit(10).all()

        return jsonify({
            "total_targets": total_targets,
            "total_findings": total_findings,
            "critical_findings": critical_findings,
            "active_scans": active_scans,
            "recent_findings": [{
                "id": f.id,
                "type": f.vuln_type,
                "severity": f.severity,
                "target": f.scan.target.domain if f.scan and f.scan.target else "unknown"
            } for f in recent_findings]
        })


@api_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "version": "1.2.0",
        "author": "ARYAN AHIRWAR (VIPHACKER.100)"
    })


@api_bp.route("/reports/generate", methods=["POST"])
def generate_report():
    data = request.json
    scan_id = data.get("scan_id")
    fmt = data.get("format", "md")

    if not scan_id:
        with SessionLocal() as db:
            latest_scan = db.query(Scan).order_by(Scan.id.desc()).first()
            if not latest_scan:
                return jsonify({"error": "No scans available to report"}), 404
            scan_id = latest_scan.id

    try:
        engine = ReportingEngine()
        filepath = engine.generate_report(scan_id, format=fmt)
        return jsonify({
            "message": "Report generated successfully",
            "filepath": filepath,
            "filename": Path(filepath).name
        })
    except (ValueError, OSError, RuntimeError) as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/reports/download/<path:filename>", methods=["GET"])
def download_report(filename):
    report_dir = str(Path("reports").resolve())
    return send_from_directory(report_dir, filename, as_attachment=True)
