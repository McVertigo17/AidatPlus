from datetime import datetime
from controllers.sakin_controller import SakinController


def test_create_sakin_and_get_active(db_session, sample_lojer_and_daire):
    daire = sample_lojer_and_daire['daire']
    session = sample_lojer_and_daire['db']

    controller = SakinController()
    data = {
        'ad_soyad': 'Ali Test',
        'daire_id': daire.id,
        'tahsis_tarihi': datetime(2025, 1, 1),
        'giris_tarihi': datetime(2025, 1, 1)
    }
    sakin = controller.create(data, db=session)
    assert sakin.id is not None
    active = controller.get_aktif_sakinler(db=session)
    assert any(s.id == sakin.id for s in active)

def test_pasif_yap_and_delete(db_session, sample_lojer_and_daire):
    daire = sample_lojer_and_daire['daire']
    session = sample_lojer_and_daire['db']
    controller = SakinController()
    data = {
        'ad_soyad': 'Mehmet Test',
        'daire_id': daire.id,
        'giris_tarihi': datetime(2025, 2, 1)
    }
    sakin = controller.create(data, db=session)
    assert sakin is not None
    # Pasif yap
    assert controller.pasif_yap(sakin.id, datetime(2025, 3, 1), db=session)
    # Aktif yap
    assert controller.aktif_yap(sakin.id, db=session)
    # Delete (soft delete)
    assert controller.delete(sakin.id, db=session)
