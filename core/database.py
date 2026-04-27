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
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("Database")

# Load configuration
config = get_config()

# Create SQLAlchemy Engine
engine: Engine = create_engine(
    config.database.url,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Verify connections are alive before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create Session Factory
SessionLocal: sessionmaker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# Declarative Base for ORM Models
Base = declarative_base()


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
