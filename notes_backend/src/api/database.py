import os
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Database configuration using environment variable with SQLite fallback.
# The environment variable name is DATABASE_URL. If not set, use local SQLite file.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notes.db")

# For SQLite, we need to pass connect_args to allow multi-threaded use in FastAPI's dev server.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


class Note(Base):
    """SQLAlchemy model for Note entity."""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


@event.listens_for(Note, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    # Automatically update the updated_at timestamp
    target.updated_at = datetime.utcnow()


def init_db() -> None:
    """Create database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy Session and ensures proper closing.

    This context manager is used by FastAPI dependency injection to provide a scoped session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
