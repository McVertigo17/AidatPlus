from controllers.hesap_controller import HesapController


def test_create_update_and_set_default(db_session):
    session = db_session
    controller = HesapController()

    data = {"ad": "Test Bank", "tur": "Banka", "bakiye": 1000.0}
    hesap = controller.create(data, db=session)
    assert hesap.id is not None
    assert abs(hesap.bakiye - 1000.0) < 0.001

    # Update bakiye
    controller.update(hesap.id, {"bakiye": 1500.0}, db=session)
    updated = controller.get_by_id(hesap.id, db=session)
    assert abs(updated.bakiye - 1500.0) < 0.001

    # Set default
    success = controller.set_varsayilan_hesap(hesap.id, db=session)
    assert success
    default = controller.get_varsayilan_hesap(db=session)
    assert default.id == hesap.id

def test_hesap_bakiye_guncelle_income_and_expense(db_session):
    session = db_session
    controller = HesapController()

    data = {"ad": "Hesap 1", "tur": "Kasa", "bakiye": 500.0}
    hesap = controller.create(data, db=session)
    # Gelir
    assert controller.hesap_bakiye_guncelle(hesap.id, 200.0, "Gelir", db=session)
    updated = controller.get_by_id(hesap.id, db=session)
    assert abs(updated.bakiye - 700.0) < 0.001

    # Gider
    assert controller.hesap_bakiye_guncelle(hesap.id, 100.0, "Gider", db=session)
    updated = controller.get_by_id(hesap.id, db=session)
    assert abs(updated.bakiye - 600.0) < 0.001
