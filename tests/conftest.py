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
    try:
        yield engine
    finally:
        # Dispose engine to ensure connections are closed
        engine.dispose()


@pytest.fixture(scope='function')
def db_session(engine):
    # Use a nested (savepoint) transaction to isolate test changes and
    # ensure the DB is clean between tests while keeping a single in-memory
    # engine for speed.
    # Ensure the DB is fresh for each test by re-initializing tables.
    from database.config import Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()
    # Start a nested transaction (SAVEPOINT) so that commits in the code
    # under test don't finalize the outer transaction and we can rollback
    # everything at the end of the test.
    session.begin_nested()

    try:
        # Monkeypatch the module-level get_db to return this session so that
        # any code that calls get_db() will use the same connection and nested
        # transaction, ensuring full isolation.
        import database.config as db_config_module
        original_get_db = db_config_module.get_db
        db_config_module.get_db = lambda: session

        yield session

        # Restore original get_db
        db_config_module.get_db = original_get_db
    finally:
        # Rollback the session and the outer transaction, then close the connection.
        session.rollback()
        session.close()
        transaction.rollback()
        connection.close()


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
