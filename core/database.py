"""DARKWIN Database Configuration & Connection Management

Provides SQLAlchemy ORM setup, session management, and database connectivity
for persistent storage of scan results, findings, and targets.

Uses LAZY initialization: the database engine is NOT connected at import time.
This means `darkwin --help`, `darkwin about`, etc. always work, even with no DB.
The connection is established the first time a DB operation is actually needed.

Exports:
    get_engine(): Returns a working Engine, connecting lazily on first call.
    get_session(): Returns a new Session, connecting lazily on first call.
    Base: Declarative base for ORM models.
    get_db(): Context manager / generator for DB sessions.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("Database")

# Load configuration (config_manager never touches DB, so this is safe)
config = get_config()


# ---------------------------------------------------------------------------
# Declarative Base for ORM Models
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    """Base class for all DARKWIN ORM models."""
    __allow_unmapped__ = True


# ---------------------------------------------------------------------------
# Lazy Engine Cache  (None until first use)
# ---------------------------------------------------------------------------
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None
_db_unavailable: bool = False   # set True after all fallbacks exhausted


def _try_primary(primary_url: str) -> Optional[Engine]:
    """Attempt a connection to the configured primary database."""
    logger.info(f"Connecting to primary database: {primary_url.split('@')[-1]}")
    try:
        eng = create_engine(primary_url, pool_pre_ping=True, pool_recycle=3600)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Connected to primary database.")
        return eng
    except Exception as e:
        err = str(e)
        if "password authentication failed" in err:
            logger.critical("❌ Database Authentication Failed!")
            logger.info("💡 Fix: align config.yaml password with docker-compose.yml")
            logger.info("   👉 Current url: " + primary_url.split('@')[-1])
            logger.info("   👉 Try: docker-compose exec postgres psql -U postgres -c \"ALTER USER darkwin WITH PASSWORD 'darkwin_pass';\"")
        elif "does not exist" in err:
            logger.critical("❌ Database / role does not exist!")
            logger.info("   👉 Try: docker-compose up -d postgres")
        elif "Connection refused" in err or "could not connect" in err.lower():
            logger.warning("⚠️  PostgreSQL server is offline.")
            logger.info("   👉 Try: docker-compose up -d postgres")
        else:
            logger.warning(f"⚠️  Primary database unreachable: {err[:200]}")
        return None


def _try_sqlite(fallback_url: str) -> Optional[Engine]:
    """Attempt a fallback connection to local SQLite."""
    logger.info(f"🔄 Attempting fallback to local SQLite: {fallback_url}")
    try:
        eng = create_engine(
            fallback_url,
            connect_args={"check_same_thread": False},
        )
        # Test that _sqlite3 C extension is present
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        # Create all tables for the fallback DB
        try:
            import core.models  # noqa: F401 — registers models with Base.metadata
            Base.metadata.create_all(bind=eng)
            logger.info("✅ SQLite database initialized with schema.")
        except Exception as schema_err:
            logger.error(f"⚠️  Could not create SQLite schema: {schema_err}")
        return eng
    except (ModuleNotFoundError, ImportError) as e:
        if "_sqlite3" in str(e):
            logger.critical("❌ Python _sqlite3 module is missing!")
            logger.info("💡 Fix 1 (SQLite): sudo apt update && sudo apt install -y libsqlite3-dev")
            logger.info("💡 Fix 2 (Recommended): Start PostgreSQL via docker-compose up -d postgres")
        else:
            logger.critical(f"❌ SQLite import error: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ SQLite fallback failed: {e}")
        return None


def get_engine() -> Engine:
    """Return a working SQLAlchemy Engine, initialising lazily on first call.

    Raises:
        RuntimeError: if neither PostgreSQL nor SQLite is available.
    """
    global _engine, _SessionLocal, _db_unavailable

    if _engine is not None:
        return _engine

    if _db_unavailable:
        raise RuntimeError(
            "No database is available. "
            "Fix PostgreSQL credentials or install libsqlite3-dev, then restart."
        )

    primary_url: str = config.database.url
    fallback_url: str = "sqlite:///darkwin.db"

    eng = _try_primary(primary_url)
    if eng is None:
        eng = _try_sqlite(fallback_url)

    if eng is None:
        _db_unavailable = True
        raise RuntimeError(
            "Database connection failed — no working fallback available.\n"
            "  • Fix PostgreSQL: check config.yaml credentials and run docker-compose up -d postgres\n"
            "  • Fix SQLite:     sudo apt install libsqlite3-dev"
        )

    _engine = eng
    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_engine,
        expire_on_commit=False,
    )
    return _engine


def get_session() -> sessionmaker:
    """Return the session factory, initialising the engine if needed."""
    global _SessionLocal
    get_engine()   # ensures _SessionLocal is set
    return _SessionLocal  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Backward-compatible SessionLocal proxy
# ---------------------------------------------------------------------------
class _LazySessionLocal:
    """Drop-in replacement for sessionmaker that connects lazily."""

    def __call__(self, *args, **kwargs) -> Session:
        return get_session()(*args, **kwargs)

    def __enter__(self):
        self._session = get_session()()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._session.rollback()
        self._session.close()
        return False


# This is what command_router.py imports — it behaves like sessionmaker() but
# delays the actual DB connection until first use.
SessionLocal = _LazySessionLocal()


# ---------------------------------------------------------------------------
# Dependency-injection generator  (for FastAPI / Flask routes)
# ---------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """Yield a database session with automatic cleanup."""
    db: Session = get_session()()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}", exc_info=True)
        raise
    finally:
        db.close()
