from controllers.kategori_yonetim_controller import KategoriYonetimController
import uuid
from models.exceptions import DuplicateError, NotFoundError, BusinessLogicError


def test_create_update_delete_ana_alt_kategori(db_session):
    session = db_session
    ctrl = KategoriYonetimController()

    # Create ana kategori
    name = f"Gelirler_{uuid.uuid4()}"
    ana = ctrl.create_ana_kategori(name, aciklama="test", tip="gelir", db=session)
    assert ana.id is not None

    # Create alt kategori
    alt = ctrl.create_alt_kategori(ana.id, "Aidat", aciklama="alt test", db=session)
    assert alt.id is not None

    # Update ana kategori
    assert ctrl.update_ana_kategori(ana.id, name + "-upd", aciklama="u", tip="gelir", db=session)

    # Delete ana kategori should fail due to existing alt category
    try:
        ctrl.delete_ana_kategori(ana.id, db=session)
        assert False, "Should have raised BusinessLogicError"
    except BusinessLogicError:
        pass

    # Remove alt and then delete ana
    session.delete(alt)
    session.commit()
    assert ctrl.delete_ana_kategori(ana.id, db=session)
