from celery import Celery
from core.config_manager import get_config
from core.logging_system import get_logger

config = get_config()
logger = get_logger("Scheduler")

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

@app.task(name="darkwin.run_scan")
def run_scan_task(target: str, pipeline_name: str, scan_id: str):
    """
    Celery task to run a specific pipeline.
    """
    logger.info(f"Worker received scan task: {scan_id} for {target} ({pipeline_name})")
    
    # Dynamic import to avoid circular dependencies
    from core.pipeline_engine import Pipeline
    # In a real implementation, we would fetch the pipeline configuration by name
    # and instantiate the Pipeline object here.
    
    # Placeholder for actual pipeline execution
    logger.info(f"Executing {pipeline_name} on {target}...")

def schedule_recurring(target, pipeline_name, interval_minutes):
    """
    Registers a periodic task with Celery Beat.
    """
    # This usually requires configuring celery_beat_schedule in settings
    logger.info(f"Scheduling recurring scan for {target} every {interval_minutes} minutes")

def cancel_schedule(target):
    """
    Cancels all pending tasks for a given target.
    """
    logger.info(f"Cancelling all scheduled scans for {target}")
    # Implementation would use app.control.revoke
