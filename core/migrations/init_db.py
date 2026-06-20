"""DARKWIN Database Initialization Script

Initializes the database schema by creating all ORM model tables.
Should be run once before first application startup.

Usage:
    python core/migrations/init_db.py
    
Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from core.database import get_engine, Base
from core.models import Target, Scan, Finding, Screenshot, Report
from core.logging_system import get_logger

logger = get_logger("DB.Init")


def init_db() -> None:
    """Initialize DARKWIN database schema.
    
    Creates all tables defined in ORM models using SQLAlchemy metadata.
    Safe to run multiple times (idempotent).
    
    Raises:
        Exception: If database connection or table creation fails.
    """
    logger.info("Initializing DARKWIN database schema...")
    
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
        logger.info(
            "Created tables: targets, scans, findings, screenshots, reports"
        )
    except (RuntimeError, OSError) as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    """Run database initialization when script is executed directly."""
    init_db()
