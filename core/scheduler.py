from celery import Celery
from core.config_manager import get_config

config = get_config()

# Initialize Celery
app = Celery(
    "darkwin",
    broker=config.redis.url,
    backend=config.redis.url
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@app.task(name="darkwin.run_module")
def run_module_task(module_name, target, scan_id, args=None, kwargs=None):
    """
    Celery task to run a specific module.
    Used for distributed scanning nodes.
    """
    from core.module_loader import get_module
    from core.database import SessionLocal
    from core.models import Finding
    
    args = args or []
    kwargs = kwargs or {}
    
    try:
        module = get_module(module_name)
        # We pass a simple dict config to the module to avoid Pydantic serialization issues in Celery
        results = module.run(target, scan_id, {})
        
        if isinstance(results, list):
            db = SessionLocal()
            for r in results:
                finding = Finding(
                    scan_id=scan_id,
                    vuln_type=r.get("vuln_type", "unknown"),
                    severity=r.get("severity", "Info"),
                    endpoint=r.get("endpoint", target),
                    payload=r.get("payload", ""),
                    description=r.get("description", "")
                )
                db.add(finding)
            db.commit()
            db.close()
            
        return {"status": "success", "findings_count": len(results)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def schedule_recurring(target, pipeline_name, interval_minutes):
    """
    Placeholder for periodic task scheduling (Step 31).
    Requires celery-beat to be configured.
    """
    pass
