import json
from configuration.config_manager import ConfigurationManager
from database.config import get_db
from models.base import Ayar


def test_loads_database_configs(db_session):
    """ConfigurationManager yüklenirken veritabanındaki ayarları okuyup merge etmelidir"""
    session = db_session

    # Ensure the singleton is reset
    ConfigurationManager._instance = None

    # Create DB ayarlar
    session.add_all([
        Ayar(anahtar='ui.theme', deger='dark', aciklama='test theme'),
        Ayar(anahtar='app.debug', deger='true', aciklama='boolean debug'),
        Ayar(anahtar='database.url', deger='sqlite:///custom.db', aciklama='custom url'),
        Ayar(anahtar='nested.config.value', deger='123', aciklama='nested int')
    ])
    session.commit()

    # Monkeypatch get_db to return our session to make sure ConfigurationManager reads the same test DB
    import database.config as db_config
    original_get_db = db_config.get_db
    db_config.get_db = lambda: session

    try:
        config = ConfigurationManager.get_instance()
        # Check parsed values
        assert config.get('ui.theme') == 'dark'
        assert config.get('app.debug') is True
        assert config.get('database.url') == 'sqlite:///custom.db'
        assert config.get('nested.config.value') == 123
    finally:
        # restore original get_db
        db_config.get_db = original_get_db
        # Reset singleton for other tests
        ConfigurationManager._instance = None
