"""DARKWIN Celery Task Scheduler & Distributed Execution

Configures Celery for distributed scanning across multiple nodes.
Provides task definitions for module execution and result persistence.

Environment Variables:
    CELERY_BROKER_URL: Redis/RabbitMQ broker URL
    CELERY_BACKEND_URL: Result backend URL
    
Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Dict, List, Any, Optional

from celery import Celery

from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("Scheduler")

config = get_config()

# Initialize Celery application
app: Celery = Celery(
    "darkwin",
    broker=config.redis.url,
    backend=config.redis.url
)

# Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
)

def _load_beat_schedule() -> Dict[str, Any]:
    """Load periodic tasks from the local schedule file."""
    import os
    import json
    schedule_file = Path("logs/schedule.json")
    beat_schedule = {}
    
    if schedule_file.exists():
        try:
            with open(schedule_file, "r") as f:
                tasks = json.load(f)
                for t in tasks:
                    if t.get("status") == "active":
                        # Convert frequency to crontab or interval
                        # Simple mapping for now: daily, weekly, monthly
                        freq = t.get("frequency", "daily").lower()
                        if freq == "daily":
                            schedule = 86400.0 # seconds
                        elif freq == "weekly":
                            schedule = 604800.0
                        elif freq == "hourly":
                            schedule = 3600.0
                        else:
                            try: schedule = float(freq)
                            except ValueError: schedule = 86400.0
                            
                        beat_schedule[f"scan_{t['id']}"] = {
                            "task": "darkwin.run_pipeline", # We'll need this task
                            "schedule": schedule,
                            "args": (t["target"], t["command"])
                        }
        except (json.JSONDecodeError, OSError, FileNotFoundError) as e:
            logger.error(f"Failed to load beat schedule: {e}")
            
    return beat_schedule

app.conf.beat_schedule = _load_beat_schedule()


@app.task(name="darkwin.run_module", bind=True, max_retries=3)
def run_module_task(
    self,
    module_name: str,
    target: str,
    scan_id: str,
    args: Optional[List[Any]] = None,
    kwargs: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute a scanner module as Celery task.
    
    Runs a specific module against a target and persists findings.
    Used for distributed scanning across multiple nodes.
    
    Args:
        module_name: Name of module to execute (e.g., "xss_scanner")
        target: Target domain/IP to scan
        scan_id: Associated scan ID
        args: Optional positional arguments for module
        kwargs: Optional keyword arguments for module
        
    Returns:
        Dict with task status and findings count:
            - status: "success" or "error"
            - findings_count: Number of findings discovered (if successful)
            - message: Error message (if failed)
            
    Raises:
        Retried up to 3 times on failure using exponential backoff.
    """
    from core.module_loader import get_module
    from core.database import SessionLocal
    from core.models import Finding
    
    args = args or []
    kwargs = kwargs or {}
    
    try:
        logger.info(
            f"🚀 Running task: {module_name} on {target} (Scan: {scan_id})"
        )
        
        # Load and execute module
        module = get_module(module_name)
        results: List[Dict[str, Any]] = module.run(target, scan_id, {})
        
        # Persist findings to database
        if isinstance(results, list) and results:
            _save_findings_to_db(scan_id, results, target)
            logger.info(f"✅ Task {module_name} completed: {len(results)} findings")
        else:
            logger.info(f"✅ Task {module_name} completed: No findings")
        
        return {
            "status": "success",
            "findings_count": len(results) if isinstance(results, list) else 0,
            "module": module_name,
            "target": target,
        }
        
    except (ValueError, OSError, ImportError) as e:
        logger.error(f"Task {module_name} failed: {e}", exc_info=True)
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


def _save_findings_to_db(
    scan_id: str,
    findings_list: List[Dict[str, Any]],
    target: str
) -> None:
    """Persist discovered findings to database.
    
    Args:
        scan_id: Associated scan ID
        findings_list: List of finding dictionaries
        target: Target that was scanned
    """
    from core.database import SessionLocal
    from core.models import Finding
    
    try:
        with SessionLocal() as db:
            for finding_data in findings_list:
                try:
                    finding: Finding = Finding(
                        scan_id=scan_id,
                        vuln_type=finding_data.get(
                            "vuln_type", finding_data.get("type", "unknown")
                        ),
                        severity=finding_data.get("severity", "Info"),
                        endpoint=finding_data.get("endpoint", target),
                        payload=finding_data.get("payload", ""),
                        description=finding_data.get("description", ""),
                        cvss_score=finding_data.get("cvss_score"),
                    )
                    db.add(finding)
                    
                except (ValueError, KeyError) as e:
                    logger.error(
                        f"Failed to persist finding for {scan_id}: {e}"
                    )

            db.commit()
            logger.info(f"Persisted {len(findings_list)} findings")

    except (OSError, RuntimeError, ImportError) as e:
        logger.error(
            f"Failed to save findings to database: {e}", exc_info=True
        )


@app.task(name="darkwin.run_pipeline")
def run_pipeline_task(target: str, pipeline_type: str) -> str:
    """Task to run a full pipeline (recon, scan, or hunt)."""
    import uuid
    import asyncio
    from core.config_manager import get_config
    from core.database import SessionLocal
    from core.models import Target, Scan
    from pipelines.recon_pipeline import get_recon_pipeline
    from pipelines.web_vuln_pipeline import get_web_vuln_pipeline
    from core.agent_loop import AgenticLoop
    
    config = get_config()
    scan_id = str(uuid.uuid4())
    logger.info(f"⏰ Starting Pipeline execution: {pipeline_type} on {target} (Scan: {scan_id})")
    
    try:
        # 1. Setup DB entries
        with SessionLocal() as db:
            target_obj = db.query(Target).filter(Target.domain == target).first()
            if not target_obj:
                target_obj = Target(domain=target, scope_confirmed=True)
                db.add(target_obj)
                db.commit()
                db.refresh(target_obj)
            
            new_scan = Scan(id=scan_id, target_id=target_obj.id, status="starting", scan_type=pipeline_type)
            db.add(new_scan)
            db.commit()

        # 2. Execute Pipeline
        if pipeline_type == "recon":
            pipeline = get_recon_pipeline(target, scan_id, config.dict())
            pipeline.run(target, scan_id)
        elif pipeline_type == "scan":
            pipeline = get_web_vuln_pipeline(target, scan_id, config.dict())
            pipeline.run(target, scan_id)
        elif pipeline_type == "hunt":
            loop = AgenticLoop(target, scan_id)
            asyncio.run(loop.run())
        else:
            raise ValueError(f"Unknown pipeline type: {pipeline_type}")
            
        return f"Completed {pipeline_type} on {target} (Scan ID: {scan_id})"
        
    except (ValueError, OSError, ImportError, RuntimeError) as e:
        logger.error(f"Failed to execute pipeline {pipeline_type}: {e}", exc_info=True)
        return f"Error: {str(e)}"
