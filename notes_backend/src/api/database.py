import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Text,
    create_engine,
    event,
) 
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Prefer Supabase Postgres via DATABASE_URL.
# IMPORTANT: Do not hardcode credentials; must be provided through environment.
# For Supabase use: postgresql+psycopg2://...:5432/postgres?sslmode=require
DATABASE_URL = os.getenv("DATABASE_URL")  # No SQLite fallback per requirement

if not DATABASE_URL:
    # Raise clear error to prompt correct env configuration in CI/runtime
    raise RuntimeError(
        "DATABASE_URL is not set. Please provide Supabase Postgres connection string in environment."
    )

# Connection args:
connect_args = {}
# Enable pool_pre_ping to avoid stale connections; SSL handled via URL (sslmode=require)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


class Note(Base):
    """SQLAlchemy model for Note entity mapped to public.notes in Supabase."""
    __tablename__ = "notes"

    # Supabase schema: id uuid pk, title text, content text, tags jsonb, is_archived boolean, created_at/updated_at timestamptz
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(Text, nullable=False, index=True)
    content = Column(Text, nullable=False)
    tags = Column(JSONB, nullable=False, default=list)  # default to [] at ORM level
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


@event.listens_for(Note, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    # Automatically update the updated_at timestamp in application as backup;
    # Supabase trigger also sets updated_at = now().
    target.updated_at = datetime.now(timezone.utc)


def init_db() -> None:
    """
    Initialize database metadata.

    For managed Supabase Postgres with RLS, DDL should be handled via migrations or SQL scripts.
    This function intentionally avoids creating tables automatically in production.
    It will attempt to reflect metadata creation only if the table exists.
    """
    try:
        # No-op for Supabase; keep function for app startup compatibility.
        # Do not call Base.metadata.create_all(bind=engine) to avoid privilege issues under RLS.
        pass
    except Exception as exc:
        # Log-friendly raise if needed by calling context
        raise RuntimeError(f"Database initialization failed: {exc}") from exc


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
