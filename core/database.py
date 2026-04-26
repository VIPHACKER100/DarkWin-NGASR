from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config_manager import get_config

# Load config to get database URL
config = get_config()

# Create Engine
engine = create_engine(config.database.url)

# Create Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
