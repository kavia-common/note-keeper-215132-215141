import os
import logging
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
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Logger for database setup messages
logger = logging.getLogger(__name__)

# Determine database URL and whether we're using Postgres (Supabase) or SQLite fallback
DATABASE_URL = os.getenv("DATABASE_URL")
USING_POSTGRES = bool(DATABASE_URL)

# If DATABASE_URL is not provided, use a local SQLite file to enable dev-only fallback
if not USING_POSTGRES:
    fallback_url = "sqlite:///./dev.db"
    DATABASE_URL = fallback_url
    logger.warning(
        "DATABASE_URL not set. Falling back to local SQLite database at %s for development. "
        "Set DATABASE_URL to your Supabase Postgres URI in production.", fallback_url
    )

# Connection args and engine setup
connect_args = {}
# For SQLite, disable check_same_thread to allow usage across threads (e.g., FastAPI)
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,  # helps avoid stale connections in Postgres
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()

# Define adapter types depending on backend.
# For SQLite, we don't have native UUID/JSONB; use TEXT for UUID and TEXT for JSON serialization via ORM defaults.
# To keep API contract intact while enabling SQLite, we will map:
# - UUID as TEXT when not using Postgres
# - JSONB as Text (storing JSON-encoded list) is not necessary if we keep Python list and let SQLAlchemy handle with SQLite (it will pickle unless specified).
#   Instead, since SQLAlchemy 2.x doesn't provide JSON for SQLite by default without extra type, we will store as Text containing JSON string? That complicates.
#   Easier approach: for SQLite, use Text and keep Python list by serializing/deserializing at the app level is overkill.
#   However, SQLAlchemy can use the generic JSON type which works across backends; but we didn't import it earlier.
# Use SQLAlchemy generic JSON for cross-dialect compatibility.
from sqlalchemy import JSON as SA_JSON  # generic JSON type works for SQLite and Postgres (maps to JSON/JSONB)

# Column type helpers
UUIDType = PG_UUID(as_uuid=True) if USING_POSTGRES else Text
JSONType = PG_JSONB if USING_POSTGRES else SA_JSON


class Note(Base):
    """SQLAlchemy model for Note entity mapped to 'notes' table.

    Uses UUID primary key for Postgres; when using SQLite fallback, stores as text.
    """
    __tablename__ = "notes"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    title = Column(Text, nullable=False, index=True)
    content = Column(Text, nullable=False)
    tags = Column(JSONType, nullable=False, default=list)  # default to [] at ORM level
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


@event.listens_for(Note, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    # Automatically update the updated_at timestamp in application as backup;
    target.updated_at = datetime.now(timezone.utc)


def init_db() -> None:
    """
    Initialize database metadata.

    Behavior:
    - If using Supabase/Postgres (DATABASE_URL provided): do NOT create tables (managed externally).
    - If using SQLite fallback: create tables locally via SQLAlchemy metadata for development convenience.
    """
    try:
        if USING_POSTGRES:
            # No-op for Supabase; avoid DDL under managed Postgres with RLS/migrations.
            logger.info("Postgres detected via DATABASE_URL. Skipping automatic DDL.")
            return
        # SQLite dev fallback: create tables if not present
        logger.info("SQLite fallback active. Creating tables if they do not exist...")
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
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
