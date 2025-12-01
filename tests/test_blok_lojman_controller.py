import uuid
from controllers.blok_controller import BlokController
from controllers.lojman_controller import LojmanController


def test_create_lojman_and_blok(db_session):
    session = db_session
    lojman_ctrl = LojmanController()
    blok_ctrl = BlokController()

    name = f"Test Lojman {uuid.uuid4()}"
    l = lojman_ctrl.create({"ad": name, "adres": "Test adres"}, db=session)
    assert l.id is not None

    bdata = {"ad": "B1", "lojman_id": l.id, "kat_sayisi": 3}
    b = blok_ctrl.create(bdata, db=session)
    assert b.id is not None
    assert b.ad == "B1"

    # get by lojman
    found = blok_ctrl.get_by_lojman(l.id, db=session)
    assert len(found) == 1

    # get by ad and lojman
    by_ad = blok_ctrl.get_by_ad_and_lojman("B1", l.id, db=session)
    assert by_ad is not None

    # update blok
    blok_ctrl.update(b.id, {"ad": "B1-Updated", "kat_sayisi": 4}, db=session)
    updated = blok_ctrl.get_by_ad_and_lojman("B1-Updated", l.id, db=session)
    assert updated.kat_sayisi == 4
