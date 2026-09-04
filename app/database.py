"""Optional SQLAlchemy session foundation.

Demo mode never creates an engine or requires a database driver.  PostgreSQL
mode is intentionally opt-in through DATABASE_URL.
"""
from __future__ import annotations
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from .config import settings

class Base(DeclarativeBase):
    pass

_engine = None
_session_factory = None

def get_engine():
    global _engine, _session_factory
    if settings.database_mode != "postgres":
        return None
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL must be configured when DATABASE_MODE=postgres")
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
        _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _engine

def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for PostgreSQL routes; never used by demo routes."""
    get_engine()
    assert _session_factory is not None
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()

def initialize_database() -> None:
    """Create mapped tables for a configured PostgreSQL development database."""
    engine = get_engine()
    if engine is not None:
        Base.metadata.create_all(bind=engine)
