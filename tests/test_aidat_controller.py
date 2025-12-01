from datetime import datetime
from controllers.aidat_controller import AidatIslemController
from controllers.sakin_controller import SakinController


def test_create_aidat_islem(db_session, sample_lojer_and_daire):
    daire = sample_lojer_and_daire['daire']
    session = sample_lojer_and_daire['db']

    aidat_controller = AidatIslemController()
    # create resident first
    sakin_controller = SakinController()
    sakin = sakin_controller.create({
        'ad_soyad': 'Ayse Test',
        'daire_id': daire.id,
        'giris_tarihi': datetime(2025, 1, 1)
    }, db=session)

    data = {
        'daire_id': daire.id,
        'ay': 12,
        'yil': 2025,
        'toplam_tutar': 1200.0,
        'son_odeme_tarihi': datetime(2025, 12, 31)
    }
    islem = aidat_controller.create(data, db=session)
    assert islem.id is not None
    res = aidat_controller.get_by_daire(daire.id, db=session)
    assert len(res) >= 1
