import pytest
from ui.aidat_panel import AidatPanel


def test_get_sakin_at_date_returns_name(db_session, sample_lojer_and_daire, monkeypatch):
    data = sample_lojer_and_daire
    session = data['db']
    daire = data['daire']

    # create a test sakin
    from models.base import Sakin
    from datetime import datetime

    s = Sakin(ad_soyad='Test Kullanici', daire_id=daire.id, tahsis_tarihi=datetime(2025,1,1))
    session.add(s)
    session.commit()

    # Monkeypatch database.config.get_db to use our session
    import database.config as db_config
    monkeypatch.setattr(db_config, 'get_db', lambda: session)

    # Create a bare AidatPanel instance without invoking BasePanel.__init__
    panel = object.__new__(AidatPanel)

    # Call the method
    name = AidatPanel.get_sakin_at_date(panel, daire_id=daire.id, yil=2025, ay=1)
    assert name == 'Test Kullanici'
