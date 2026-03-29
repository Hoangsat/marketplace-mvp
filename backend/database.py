# database.py
# Sets up SQLAlchemy engine, session factory and base class.
# All models import Base from here.

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./marketpy.db")

# connect_args is needed for SQLite only (allows multi-thread use in FastAPI)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _sqlite_db_file_path() -> str | None:
    """Resolve absolute path to the SQLite file for DATABASE_URL, or None if not SQLite."""
    if not DATABASE_URL.startswith("sqlite"):
        return None
    rest = DATABASE_URL[len("sqlite:///") :]
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if rest.startswith("./"):
        return os.path.normpath(os.path.join(backend_dir, rest[2:]))
    if os.path.isabs(rest):
        return os.path.normpath(rest)
    return os.path.normpath(os.path.join(backend_dir, rest))


def reset_sqlite_dev_database_if_needed() -> None:
    """
    In development only: clear existing SQLite data so create_all() can rebuild
    tables that match current models. Uses DROP ALL TABLES (no file delete) so
    Windows does not hit WinError 32 when another process held the file.

    Never runs when ENV=production. Safe when the DB file does not exist yet.
    """
    if os.getenv("ENV") == "production":
        return
    db_path = _sqlite_db_file_path()
    if not db_path:
        return

    # Register all models on Base.metadata before drop_all.
    import models.models  # noqa: F401

    if not os.path.isfile(db_path):
        return

    print(
        "=== DEVELOPMENT MODE: Removing old database to apply schema changes ===",
        flush=True,
    )
    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    print(f"Old database file removed: {os.path.basename(db_path)}", flush=True)
