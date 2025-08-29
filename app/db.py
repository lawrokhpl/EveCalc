import contextlib
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


_engine = None
_SessionLocal = None


def _build_sqlalchemy_url() -> str:
    """Build a SQLAlchemy URL.

    Priority:
    1) Cloud SQL Connector (if CLOUD_SQL_CONNECTION_NAME set) – pg8000 driver
    2) Direct TCP to Postgres if DB_HOST provided
    3) SQLite fallback for local development
    """
    if settings.CLOUD_SQL_CONNECTION_NAME and settings.DB_USER and settings.DB_PASS and settings.DB_NAME:
        # Cloud SQL Connector for Postgres with pg8000
        # Format: postgresql+pg8000://USER:PASSWORD@/DB?unix_sock=/cloudsql/INSTANCE/.s.PGSQL.5432
        return (
            f"postgresql+pg8000://{settings.DB_USER}:{settings.DB_PASS}"
            f"@/{settings.DB_NAME}?unix_sock=/cloudsql/{settings.CLOUD_SQL_CONNECTION_NAME}/.s.PGSQL.5432"
        )

    if settings.DB_HOST and settings.DB_USER and settings.DB_PASS and settings.DB_NAME:
        return (
            f"postgresql+pg8000://{settings.DB_USER}:{settings.DB_PASS}"
            f"@{settings.DB_HOST}/{settings.DB_NAME}"
        )

    # Fallback: local SQLite (dev only)
    return f"sqlite:///{settings.SQLITE_PATH}"


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        url = _build_sqlalchemy_url()
        # Cloud SQL/managed envs can drop idle connections; recycle and pre-ping
        _engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=2,
            future=True,
        )
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine


def get_session() -> Generator:
    get_engine()
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextlib.contextmanager
def session_scope() -> Generator:
    """Context manager for a SQLAlchemy session scope."""
    gen = get_session()
    sess: Optional[object] = None
    try:
        sess = next(gen)
        yield sess
        try:
            next(gen)
        except StopIteration:
            pass
    except Exception:
        raise


