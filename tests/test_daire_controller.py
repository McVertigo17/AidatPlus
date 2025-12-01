from controllers.daire_controller import DaireController
from controllers.sakin_controller import SakinController
from controllers.blok_controller import BlokController
from controllers.lojman_controller import LojmanController
import uuid
from datetime import datetime


def test_daire_crud_and_queries(db_session):
    session = db_session
    lojman_ctrl = LojmanController()
    blok_ctrl = BlokController()
    daire_ctrl = DaireController()
    sakin_ctrl = SakinController()

    name = f"Test Lojman {uuid.uuid4()}"
    l = lojman_ctrl.create({"ad": name, "adres": "Test adres"}, db=session)
    b = blok_ctrl.create({"ad": "B2", "lojman_id": l.id, "kat_sayisi": 2}, db=session)

    d = daire_ctrl.create({"daire_no": "201", "blok_id": b.id, "kat": 2, "kiraya_esas_alan": 80.0}, db=session)
    assert d.id is not None

    # get by no and blok
    found = daire_ctrl.get_by_no_and_blok("201", b.id, db=session)
    assert found is not None

    # Create Sakin and test dolu/boş
    sakin = sakin_ctrl.create({"ad_soyad": "Test Sakin", "daire_id": d.id, "giris_tarihi": datetime(2025, 1, 1)}, db=session)

    dolu = daire_ctrl.get_dolu_daireler(db=session)
    assert len(dolu) >= 1
    bos = daire_ctrl.get_bos_daireler(db=session)
    # There should be no infinite assumption: check at least one method returns list
    assert isinstance(bos, list)

    # get all with details
    all_with_details = daire_ctrl.get_all_with_details(db=session)
    assert isinstance(all_with_details, list)

    # update daire
    daire_ctrl.update(d.id, {"daire_no": "202"}, db=session)
    updated = daire_ctrl.get_by_no_and_blok("202", b.id, db=session)
    assert updated is not None
