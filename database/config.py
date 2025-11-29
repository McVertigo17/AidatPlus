"""
Veritabanı konfigürasyonu
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

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

def create_tables() -> None:
    """Veritabanı tablolarını oluştur"""
    Base.metadata.create_all(bind=engine)

def init_database() -> None:
    """Veritabanını başlat"""
    create_tables()