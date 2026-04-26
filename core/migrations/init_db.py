import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.database import engine, Base
from core.models import Target, Scan, Finding, Screenshot, Report
from core.logging_system import get_logger

logger = get_logger("InitDB")

def init_db():
    logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
