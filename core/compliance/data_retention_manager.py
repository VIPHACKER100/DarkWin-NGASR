import datetime
import os
from core.database import SessionLocal
from core.models import Scan, Finding, Report, Screenshot
from core.logging_system import get_logger

logger = get_logger("Compliance.Retention")

def enforce_retention(days: int = 90):
    """Deletes scans and findings older than the specified retention period.
    
    Also attempts to remove associated physical files (reports, screenshots).
    """
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    logger.info(f"🧹 Enforcing data retention policy (Cutoff: {cutoff.isoformat()}, {days} days)")

    with SessionLocal() as db:
        try:
            # 1. Find scans to delete
            old_scans = db.query(Scan).filter(Scan.started_at < cutoff).all()
            scan_count = len(old_scans)
            
            if scan_count == 0:
                logger.info("✅ No old data to purge.")
                return

            for scan in old_scans:
                # 2. Cleanup physical files associated with screenshots
                screenshots = db.query(Screenshot).filter(Screenshot.scan_id == scan.id).all()
                for ss in screenshots:
                    if os.path.exists(ss.filepath):
                        try:
                            os.remove(ss.filepath)
                        except Exception as e:
                            logger.error(f"Failed to delete screenshot file {ss.filepath}: {e}")
                
                # 3. Cleanup physical files associated with reports
                reports = db.query(Report).filter(Report.scan_id == scan.id).all()
                for report in reports:
                    if os.path.exists(report.filepath):
                        try:
                            os.remove(report.filepath)
                        except Exception as e:
                            logger.error(f"Failed to delete report file {report.filepath}: {e}")

                # 4. Delete DB records (Cascade delete should handle findings/screenshots if configured)
                # If not configured, we do it manually
                db.query(Finding).filter(Finding.scan_id == scan.id).delete()
                db.query(Screenshot).filter(Screenshot.scan_id == scan.id).delete()
                db.query(Report).filter(Report.scan_id == scan.id).delete()
                db.delete(scan)

            db.commit()
            logger.info(f"✨ Successfully purged {scan_count} old scans and associated data.")
            
        except Exception as e:
            db.rollback()
            logger.error(f"💥 Data retention enforcement failed: {e}")

