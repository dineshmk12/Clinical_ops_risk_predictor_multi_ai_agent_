from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    """Open a session and guarantee it's closed — used by the mock MCP
    servers (mcp_servers/*.py) to replace their repeated
    SessionLocal()/try/finally boilerplate."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
