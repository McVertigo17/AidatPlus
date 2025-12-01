import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database.config import Base
from datetime import datetime


@pytest.fixture(scope='session')
def engine():
    # Use StaticPool for in-memory SQLite so that the same connection is used across sessions
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    # Ensure models are imported so tables are registered before create_all
    import models.base  # noqa: F401
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope='function')
def db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_lojer_and_daire(db_session):
    from models.base import Lojman, Blok, Daire
    import uuid

    # Create Lojman
    lojman = Lojman(ad=f'Test Lojman {uuid.uuid4()}', adres='Test adres')
    db_session.add(lojman)
    db_session.flush()

    # Create Blok
    blok = Blok(ad='A', kat_sayisi=3, lojman_id=lojman.id)
    db_session.add(blok)
    db_session.flush()

    # Create Daire
    daire = Daire(daire_no='101', blok_id=blok.id, kat=1, kiraya_esas_alan=75.0, isitilan_alan=75.0)
    db_session.add(daire)
    db_session.commit()
    db_session.refresh(daire)

    return {
        'lojman': lojman,
        'blok': blok,
        'daire': daire,
        'db': db_session
    }
