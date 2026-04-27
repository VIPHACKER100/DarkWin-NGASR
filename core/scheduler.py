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
        
    except Exception as e:
        logger.error(f"❌ Task {module_name} failed: {e}", exc_info=True)
        
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
                    
                except Exception as e:
                    logger.error(
                        f"Failed to persist finding for {scan_id}: {e}"
                    )
            
            db.commit()
            logger.info(f"💾 Persisted {len(findings_list)} findings")
            
    except Exception as e:
        logger.error(
            f"Failed to save findings to database: {e}", exc_info=True
        )


def schedule_recurring(
    target: str,
    pipeline_name: str,
    interval_minutes: int
) -> None:
    """Schedule periodic scanning task.
    
    Requires celery-beat to be running for periodic task execution.
    
    Args:
        target: Target to scan
        pipeline_name: Pipeline name to execute
        interval_minutes: Interval in minutes between scans
        
    Note:
        This is a placeholder. Full implementation requires celery-beat
        configuration and database-backed scheduler.
    """
    logger.info(
        f"Scheduling recurring scan: {pipeline_name} on {target} "
        f"every {interval_minutes} minutes"
    )
    # TODO: Implement with celery-beat
