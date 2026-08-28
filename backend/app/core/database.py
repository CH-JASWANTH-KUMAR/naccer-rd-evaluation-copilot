from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Configure SQLAlchemy engine with proper pool handling
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base ORM class for SQLAlchemy 2.x models."""


def get_db() -> Generator:
    """Reusable database session dependency with proper lifecycle management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
