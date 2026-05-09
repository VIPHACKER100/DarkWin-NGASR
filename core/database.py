"""DARKWIN Database Configuration & Connection Management

Provides SQLAlchemy ORM setup, session management, and database connectivity
for persistent storage of scan results, findings, and targets.

Exports:
    engine: SQLAlchemy engine instance
    SessionLocal: Session factory for database transactions
    Base: Declarative base for ORM models
    get_db(): Dependency injection generator for FastAPI/Flask
    
Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("Database")

# Load configuration
config = get_config()

# Declarative Base for ORM Models
class Base(DeclarativeBase):
    """Base class for all DARKWIN ORM models.
    
    Includes __allow_unmapped__=True to support legacy annotations
    if necessary, though modern Mapped[] annotations are preferred.
    """
    __allow_unmapped__ = True


# Create SQLAlchemy Engine with Fallback Support
def create_robust_engine() -> Engine:
    """Create a database engine with automatic fallback to SQLite.
    
    Tries the configured database URL first. If connection fails
    (e.g., PostgreSQL is offline), falls back to local SQLite.
    """
    primary_url = config.database.url
    fallback_url = "sqlite:///darkwin.db"
    
    try:
        # Try primary connection
        logger.info(f"Connecting to primary database: {primary_url.split('@')[-1]}")
        temp_engine = create_engine(
            primary_url,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        # Test the connection immediately
        with temp_engine.connect() as conn:
            logger.info("✅ Connected to primary database.")
            return temp_engine
            
    except Exception as e:
        logger.warning(f"⚠️ Primary database unreachable: {e}")
        logger.info(f"🔄 Attempting fallback to local SQLite: {fallback_url}")
        
        try:
            sqlite_engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False} if "sqlite" in fallback_url else {}
            )
            
            # Test SQLite engine creation and table setup
            try:
                # Import models to register them with Base.metadata
                import core.models
                Base.metadata.create_all(bind=sqlite_engine)
                logger.info("✅ SQLite database initialized with schema.")
            except Exception as err:
                logger.error(f"❌ Failed to initialize SQLite schema: {err}")
                
            return sqlite_engine
            
        except (ModuleNotFoundError, ImportError) as sqlite_err:
            if "_sqlite3" in str(sqlite_err):
                logger.critical("❌ Critical Error: Python SQLite module is missing!")
                logger.info("💡 To fix SQLite: sudo apt update && sudo apt install -y libsqlite3-dev")
                logger.info("💡 Or start the primary database (Recommended):")
                logger.info("   👉 Run: docker-compose up -d postgres")
                logger.info("   👉 Or:  sudo service postgresql start")
            else:
                logger.critical(f"❌ SQLite fallback failed: {sqlite_err}")
            
            # If everything fails, we can't really proceed safely
            # But we'll raise a clearer error
            raise RuntimeError("Database connection failed and no working fallback available.") from sqlite_err
        except Exception as fallback_err:
            logger.critical(f"❌ Database fallback failed: {fallback_err}")
            raise

engine: Engine = create_robust_engine()

# Create Session Factory
SessionLocal: sessionmaker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup.
    
    Yields a SQLAlchemy session and ensures it's closed after use.
    Suitable for use as FastAPI/Flask dependency.
    
    Yields:
        SQLAlchemy Session instance for database operations.
        
    Example:
        with get_db() as db:
            results = db.query(Target).all()
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}", exc_info=True)
        raise
    finally:
        db.close()
