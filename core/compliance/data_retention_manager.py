"""DARKWIN Data Retention Manager compliance module.

Enforces data retention policies by deleting scans, findings, and
associated physical files older than the configured cutoff period.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import datetime
from pathlib import Path

from core.database import SessionLocal
from core.logging_system import get_logger
from core.models import Finding, Report, Scan, Screenshot

logger = get_logger("Compliance.Retention")


def enforce_retention(days: int = 90) -> None:
    """Delete scans and findings older than *days*.

    Also removes associated physical files (reports, screenshots).

    Args:
        days: Retention period in days (default 90).
    """
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    logger.info(f"Enforcing data retention policy (Cutoff: {cutoff.isoformat()}, {days} days)")

    with SessionLocal() as db:
        try:
            old_scans = db.query(Scan).filter(Scan.started_at < cutoff).all()
            scan_count = len(old_scans)

            if scan_count == 0:
                logger.info("No old data to purge.")
                return

            for scan in old_scans:
                for ss in db.query(Screenshot).filter(Screenshot.scan_id == scan.id).all():
                    try:
                        Path(ss.filepath).unlink(missing_ok=True)
                    except OSError as e:
                        logger.error(f"Failed to delete screenshot file {ss.filepath}: {e}")

                for report in db.query(Report).filter(Report.scan_id == scan.id).all():
                    try:
                        Path(report.filepath).unlink(missing_ok=True)
                    except OSError as e:
                        logger.error(f"Failed to delete report file {report.filepath}: {e}")

                db.query(Finding).filter(Finding.scan_id == scan.id).delete()
                db.query(Screenshot).filter(Screenshot.scan_id == scan.id).delete()
                db.query(Report).filter(Report.scan_id == scan.id).delete()
                db.delete(scan)

            db.commit()
            logger.info(f"Successfully purged {scan_count} old scans and associated data.")

        except (OSError, RuntimeError, ImportError) as e:
            db.rollback()
            logger.error(f"Data retention enforcement failed: {e}")

