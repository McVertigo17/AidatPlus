import os
import tempfile
import shutil
from pathlib import Path
from controllers.backup_controller import BackupController
from models.base import Lojman, Blok, Daire, Sakin, Hesap
import pandas as pd


def test_backup_excel_and_restore(sample_lojer_and_daire, db_session, tmp_path, monkeypatch):
    data = sample_lojer_and_daire
    db = data['db']
    # create additional sample data
    sakin = Sakin(ad_soyad='Test Sakin', daire_id=data['daire'].id)
    db.add(sakin)
    hesap = Hesap(ad='Test Hesap', tur='Nakit', bakiye=1000.0)
    db.add(hesap)
    db.commit()

    controller = BackupController()
    controller.db = db
    # ensure controller uses test DB session
    import database.config as db_config
    monkeypatch.setattr(db_config, 'get_db', lambda: db)
    # monkeypatch controller._get_db to ensure it returns our test session
    monkeypatch.setattr(BackupController, '_get_db', lambda self: db)

    assert controller._get_db() is db
    # verify engine has the table and sqlite_master shows it
    from sqlalchemy import inspect as sa_inspect
    tables = sa_inspect(db.bind).get_table_names()
    assert 'lojmanlar' in tables
    # verify sqlite_master entries show table on same connection
    result = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [r[0] for r in result]
    assert 'lojmanlar' in table_names
    info = controller.get_database_info()
    assert 'lojmanlar' in info
    assert info['lojmanlar'] >= 1
    # direct query via session works
    assert db.query(Lojman).count() >= 1

    # backup to excel
    # verify model classes match expected definitions
    assert controller.MODELS_ORDER[0] is Lojman
    excel_file = tmp_path / 'backup_test.xlsx'
    assert controller.backup_to_excel(str(excel_file))
    assert excel_file.exists()

    # confirm the excel has sheet for lojmanlar and daireler
    xls = pd.ExcelFile(excel_file)
    assert 'lojmanlar' in xls.sheet_names
    assert 'daireler' in xls.sheet_names

    # reset database and ensure tables are empty
    controller.db = db
    assert controller.reset_database() is True
    controller.db = db
    info = controller.get_database_info()
    assert info == {}

    # restore from excel
    controller.db = db
    assert controller.restore_from_excel(str(excel_file)) is True
    # verify counts restored
    controller.db = db
    info = controller.get_database_info()
    assert 'lojmanlar' in info and info['lojmanlar'] >= 1


def test_backup_xml_and_restore(sample_lojer_and_daire, db_session, tmp_path, monkeypatch):
    data = sample_lojer_and_daire
    db = data['db']
    # create additional sample data
    sakin = Sakin(ad_soyad='XML Sakin', daire_id=data['daire'].id)
    db.add(sakin)
    db.commit()

    controller = BackupController()
    import database.config as db_config
    monkeypatch.setattr(db_config, 'get_db', lambda: db)
    controller.db = db

    xml_file = tmp_path / 'backup_test.xml'
    assert controller.backup_to_xml(str(xml_file)) is True
    assert xml_file.exists()

    # basic check: xml contains Tablo elements for lojmanlar
    content = xml_file.read_text(encoding='utf-8')
    assert '<Tablo ad="lojmanlar">' in content

    # reset and restore
    controller.db = db
    assert controller.reset_database()
    controller.db = db
    assert controller.restore_from_xml(str(xml_file)) is True
    controller.db = db
    info = controller.get_database_info()
    assert 'lojmanlar' in info and info['lojmanlar'] >= 1


def test_backup_database_file(monkeypatch, tmp_path):
    controller = BackupController()

    # Create a dummy aidat_plus.db file in cwd
    proj_db = Path(os.getcwd()) / 'aidat_plus.db'
    proj_db.write_text('dummy')

    try:
        # choose a target directory
        target_dir = tmp_path
        assert controller.backup_database_file(str(target_dir)) is True

        # Confirm that a backup file was copied
        backups = list(target_dir.glob('aidat_plus_backup_*.db'))
        assert len(backups) >= 1
    finally:
        if proj_db.exists():
            proj_db.unlink()
