import warnings
import gc
import pandas as pd
from controllers.backup_controller import BackupController


def test_backup_to_excel_no_resource_warnings(sample_lojer_and_daire, db_session, tmp_path, monkeypatch):
    """Ensure backup_to_excel does not emit ResourceWarning for unclosed files."""
    data = sample_lojer_and_daire
    db = data['db']

    monkeypatch.setattr('database.config.get_db', lambda: db)

    bc = BackupController()
    bc.db = db
    excel_file = tmp_path / 'backup_res_warnings.xlsx'

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        assert bc.backup_to_excel(str(excel_file)) is True
        # force garbage collection to trigger any pending ResourceWarning
        gc.collect()

    # No ResourceWarning should be emitted
    assert not any(issubclass(x.category, ResourceWarning) for x in w)
