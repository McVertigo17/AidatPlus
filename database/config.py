"""
Veritabanı konfigürasyonu
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# Veritabanı dosyası
DATABASE_URL = "sqlite:///./aidat_plus.db"

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite için gerekli
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Session:
    """Veritabanı oturumu döndür"""
    return SessionLocal()


@contextmanager
def get_db_session() -> Session:
    """Context manager for DB sessions: yields a session and ensures it is closed.

    If `get_db()` is monkeypatched (e.g., in tests), this returns that session but will not close it.
    This function closes the session only when the session's bind is the module-level `engine`.
    """
    db = get_db()
    try:
        yield db
    finally:
        try:
            if hasattr(db, 'bind') and db.bind is engine:
                db.close()
        except Exception:
            # Best effort close; swallow exceptions to avoid masking the real error
            pass

def create_tables() -> None:
    """Veritabanı tablolarını oluştur"""
    Base.metadata.create_all(bind=engine)

def init_database() -> None:
    """Veritabanını başlat"""
    create_tables()