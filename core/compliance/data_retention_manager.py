import datetime
from core.database import SessionLocal
from core.models import Scan, Finding

def enforce_retention(days: int = 90):
    """
    Deletes scans and findings older than the specified retention period.
    """
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    with SessionLocal() as db:
        # Implementation would delete records older than cutoff
        pass
