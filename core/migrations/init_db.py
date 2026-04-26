from core.database import engine, Base
from core.models import Target, Scan, Finding, Screenshot, Report
from core.logging_system import get_logger

logger = get_logger("DB.Init")

def init_db():
    logger.info("Initializing DARKWIN database...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

if __name__ == "__main__":
    init_db()
