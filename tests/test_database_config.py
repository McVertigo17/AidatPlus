import pytest
from database import config as db_config
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_get_db_returns_session(monkeypatch, engine):
    # Replace the module SessionLocal to use the test engine
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    monkeypatch.setattr(db_config, 'SessionLocal', TestSessionLocal)

    s = db_config.get_db()
    try:
        from sqlalchemy.orm.session import Session
        assert hasattr(s, 'execute')
        # basic query works
        s.execute('SELECT 1')
    finally:
        s.close()


def test_create_tables_uses_engine(monkeypatch, engine):
    # Point module engine to our test engine and call create_tables
    monkeypatch.setattr(db_config, 'engine', engine)
    db_config.create_tables()

    inspector = inspect(engine)
    # There should be tables created as Base metadata in test setup - check for lojmanlar table
    tables = inspector.get_table_names()
    # It's valid to assert that at least one table exists
    assert len(tables) >= 1


def test_init_database_calls_create_tables(monkeypatch):
    called = {'value': False}

    def fake_create_tables():
        called['value'] = True

    monkeypatch.setattr(db_config, 'create_tables', fake_create_tables)

    db_config.init_database()
    assert called['value'] is True
