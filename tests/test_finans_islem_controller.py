from controllers.finans_islem_controller import FinansIslemController
from controllers.hesap_controller import HesapController
from datetime import datetime
from models.exceptions import NotFoundError


def test_create_income_and_expense_and_transfer(db_session):
    session = db_session
    hesap_ctrl = HesapController()
    finans_ctrl = FinansIslemController()

    # Create accounts
    h1 = hesap_ctrl.create({"ad": "H1", "tur": "Banka", "bakiye": 1000.0}, db=session)
    h2 = hesap_ctrl.create({"ad": "H2", "tur": "Kasa", "bakiye": 500.0}, db=session)

    # Create income
    income = finans_ctrl.create({
        "tur": "Gelir",
        "tutar": 200.0,
        "hesap_id": h1.id,
        "tarih": datetime(2025, 1, 1)
    }, db=session)
    assert income.id is not None
    # Verify balance updated
    updated_h1 = hesap_ctrl.get_by_id(h1.id, db=session)
    assert abs(updated_h1.bakiye - 1200.0) < 0.001

    # Create expense
    expense = finans_ctrl.create({
        "tur": "Gider",
        "tutar": 100.0,
        "hesap_id": h1.id,
        "tarih": datetime(2025, 1, 2)
    }, db=session)
    updated_h1 = hesap_ctrl.get_by_id(h1.id, db=session)
    assert abs(updated_h1.bakiye - 1100.0) < 0.001

    # Create transfer
    transfer = finans_ctrl.create({
        "tur": "Transfer",
        "tutar": 200.0,
        "hesap_id": h1.id,
        "hedef_hesap_id": h2.id,
        "tarih": datetime(2025, 1, 3)
    }, db=session)
    updated_h1 = hesap_ctrl.get_by_id(h1.id, db=session)
    updated_h2 = hesap_ctrl.get_by_id(h2.id, db=session)
    assert abs(updated_h1.bakiye - 900.0) < 0.001
    assert abs(updated_h2.bakiye - 700.0) < 0.001

def test_update_with_balance_adjustment_and_delete(db_session):
    session = db_session
    hesap_ctrl = HesapController()
    finans_ctrl = FinansIslemController()

    h1 = hesap_ctrl.create({"ad": "H3", "tur": "Banka", "bakiye": 1000.0}, db=session)

    islem = finans_ctrl.create({
        "tur": "Gelir",
        "tutar": 300.0,
        "hesap_id": h1.id,
        "tarih": datetime(2025, 2, 1)
    }, db=session)
    # Now update to a different amount
    finans_ctrl.update_with_balance_adjustment(islem.id, {"tutar": 400.0}, db=session)
    updated = finans_ctrl.get_by_hesap(h1.id, db=session)[0]
    assert abs(updated.tutar - 400.0) < 0.001
    # Delete the transaction and check balance deduction
    finans_ctrl.delete(updated.id, db=session)
    hesap_after = hesap_ctrl.get_by_id(h1.id, db=session)
    # Since it was a Gelir of 400, deleting should subtract 400
    assert abs(hesap_after.bakiye - 1000.0) < 0.001


def test_transfer_with_insufficient_balance_allows_negative(db_session):
    session = db_session
    hesap_ctrl = HesapController()
    finans_ctrl = FinansIslemController()

    # Source has low balance
    h_src = hesap_ctrl.create({"ad": "H_SRC", "tur": "Banka", "bakiye": 50.0}, db=session)
    h_dst = hesap_ctrl.create({"ad": "H_DST", "tur": "Banka", "bakiye": 0.0}, db=session)

    # Transfer more than available
    transfer = finans_ctrl.create({
        "tur": "Transfer",
        "tutar": 100.0,
        "hesap_id": h_src.id,
        "hedef_hesap_id": h_dst.id,
        "tarih": datetime(2025, 3, 1)
    }, db=session)

    assert transfer.id is not None
    updated_src = hesap_ctrl.get_by_id(h_src.id, db=session)
    updated_dst = hesap_ctrl.get_by_id(h_dst.id, db=session)
    # Source should be negative (50 - 100)
    assert abs(updated_src.bakiye - (-50.0)) < 0.001
    # Destination increased
    assert abs(updated_dst.bakiye - 100.0) < 0.001


def test_transfer_balance_update_failure_propagates_and_islem_persists(db_session, monkeypatch):
    session = db_session
    hesap_ctrl = HesapController()
    finans_ctrl = FinansIslemController()

    h_src = hesap_ctrl.create({"ad": "H4", "tur": "Banka", "bakiye": 500.0}, db=session)
    h_dst = hesap_ctrl.create({"ad": "H5", "tur": "Banka", "bakiye": 200.0}, db=session)

    # Monkeypatch hesap_bakiye_guncelle to raise exception on update
    def raise_error(self, hesap_id, tutar, islem_turu, db=None):
        raise RuntimeError("Simulated balance update failure")

    monkeypatch.setattr(HesapController, 'hesap_bakiye_guncelle', raise_error)

    try:
        try:
            finans_ctrl.create({
                "tur": "Transfer",
                "tutar": 100.0,
                "hesap_id": h_src.id,
                "hedef_hesap_id": h_dst.id,
                "tarih": datetime(2025, 4, 1)
            }, db=session)
            assert False, "Expected RuntimeError due to monkeypatched hesap_bakiye_guncelle"
        except RuntimeError:
            # Exception propagated as expected
            pass

        # Transaction record was committed first; ensure the FinansIslem exists
        txs = finans_ctrl.get_transferler(db=session)
        assert any(tx.hedef_hesap_id == h_dst.id and tx.hesap_id == h_src.id for tx in txs)

        # Balances should remain unchanged because balance update failed
        s_after = hesap_ctrl.get_by_id(h_src.id, db=session)
        d_after = hesap_ctrl.get_by_id(h_dst.id, db=session)
        assert abs(s_after.bakiye - 500.0) < 0.001
        assert abs(d_after.bakiye - 200.0) < 0.001
    finally:
        # restore method (monkeypatch will be undone automatically by fixture cleanup)
        pass


def test_create_with_invalid_kategori_raises_notfound(db_session):
    session = db_session
    finans_ctrl = FinansIslemController()

    # Create a test account
    from controllers.hesap_controller import HesapController as HC
    hesap_ctrl = HC()
    h = hesap_ctrl.create({"ad": "K_Acc", "tur": "Banka", "bakiye": 100.0}, db=session)

    try:
        finans_ctrl.create({
            "tur": "Gelir",
            "tutar": 50.0,
            "hesap_id": h.id,
            "kategori_id": 99999,  # non-existent
            "tarih": datetime(2025, 5, 1)
        }, db=session)
        assert False, "Expected NotFoundError due to non-existent category"
    except NotFoundError:
        pass


def test_delete_transfer_reverses_balances(db_session):
    session = db_session
    hesap_ctrl = HesapController()
    finans_ctrl = FinansIslemController()

    h1 = hesap_ctrl.create({"ad": "Hdel1", "tur": "Banka", "bakiye": 500.0}, db=session)
    h2 = hesap_ctrl.create({"ad": "Hdel2", "tur": "Banka", "bakiye": 200.0}, db=session)

    tx = finans_ctrl.create({
        "tur": "Transfer",
        "tutar": 150.0,
        "hesap_id": h1.id,
        "hedef_hesap_id": h2.id,
        "tarih": datetime(2025, 6, 1)
    }, db=session)

    # Ensure balances updated
    h1a = hesap_ctrl.get_by_id(h1.id, db=session)
    h2a = hesap_ctrl.get_by_id(h2.id, db=session)
    assert abs(h1a.bakiye - 350.0) < 0.001
    assert abs(h2a.bakiye - 350.0) < 0.001

    # Delete transaction and ensure balances reversed
    finans_ctrl.delete(tx.id, db=session)
    h1b = hesap_ctrl.get_by_id(h1.id, db=session)
    h2b = hesap_ctrl.get_by_id(h2.id, db=session)
    assert abs(h1b.bakiye - 500.0) < 0.001
    assert abs(h2b.bakiye - 200.0) < 0.001


def test_update_transfer_to_gider_and_adjust_balances(db_session):
    """Test updating a Transfer to a Gider (expense) with correct balance adjustment.
    
    Scenario:
    1. Create s=500, d=100
    2. Create Transfer(50): s=450, d=150
    3. Convert Transfer to Gider with new_tutar=50:
       - Revert transfer: s=500, d=100 (reverse the transfer effect)
       - Apply new Gider: s=450 (500-50), d=100 (unchanged)
    """
    session = db_session
    hesap_ctrl = HesapController()
    finans_ctrl = FinansIslemController()

    # Create accounts and create a transfer
    s = hesap_ctrl.create({"ad": "HT1", "tur": "Banka", "bakiye": 500.0}, db=session)
    d = hesap_ctrl.create({"ad": "HT2", "tur": "Banka", "bakiye": 100.0}, db=session)

    tx = finans_ctrl.create({
        "tur": "Transfer",
        "tutar": 50.0,
        "hesap_id": s.id,
        "hedef_hesap_id": d.id,
        "tarih": datetime(2025, 7, 1)
    }, db=session)

    # Verify after transfer
    s_after_transfer = hesap_ctrl.get_by_id(s.id, db=session)
    d_after_transfer = hesap_ctrl.get_by_id(d.id, db=session)
    assert abs(s_after_transfer.bakiye - 450.0) < 0.001
    assert abs(d_after_transfer.bakiye - 150.0) < 0.001

    # Now convert the transfer to a Gider (expense) on source account
    finans_ctrl.update_with_balance_adjustment(tx.id, {"tur": "Gider", "hedef_hesap_id": None}, db=session)

    s_final = hesap_ctrl.get_by_id(s.id, db=session)
    d_final = hesap_ctrl.get_by_id(d.id, db=session)

    # After conversion:
    # - Revert transfer: s=500, d=100
    # - Apply new Gider(50): s=450, d=100 (target not affected)
    assert abs(s_final.bakiye - 450.0) < 0.001
    assert abs(d_final.bakiye - 100.0) < 0.001


def test_update_transfer_to_gelir_and_adjust_balances(db_session):
    """Test updating a Transfer to a Gelir (income) with correct balance adjustment.
    
    Scenario:
    1. Create s=500, d=100
    2. Create Transfer(50): s=450, d=150
    3. Convert Transfer to Gelir with tutar=60:
       - Revert transfer: s=500, d=100
       - Apply new Gelir(60): s=560, d=100 (target not affected)
    """
    session = db_session
    hesap_ctrl = HesapController()
    finans_ctrl = FinansIslemController()

    s = hesap_ctrl.create({"ad": "HTG1", "tur": "Banka", "bakiye": 500.0}, db=session)
    d = hesap_ctrl.create({"ad": "HTG2", "tur": "Banka", "bakiye": 100.0}, db=session)

    tx = finans_ctrl.create({
        "tur": "Transfer",
        "tutar": 50.0,
        "hesap_id": s.id,
        "hedef_hesap_id": d.id,
        "tarih": datetime(2025, 7, 1)
    }, db=session)

    # Verify after transfer
    s_after_transfer = hesap_ctrl.get_by_id(s.id, db=session)
    d_after_transfer = hesap_ctrl.get_by_id(d.id, db=session)
    assert abs(s_after_transfer.bakiye - 450.0) < 0.001
    assert abs(d_after_transfer.bakiye - 150.0) < 0.001

    # Convert transfer to Gelir with different amount (60)
    finans_ctrl.update_with_balance_adjustment(tx.id, {"tur": "Gelir", "hedef_hesap_id": None, "tutar": 60.0}, db=session)

    s_final = hesap_ctrl.get_by_id(s.id, db=session)
    d_final = hesap_ctrl.get_by_id(d.id, db=session)

    # After conversion:
    # - Revert transfer: s=500, d=100
    # - Apply new Gelir(60): s=560, d=100 (target not affected)
    assert abs(s_final.bakiye - 560.0) < 0.001
    assert abs(d_final.bakiye - 100.0) < 0.001


def test_update_gider_to_transfer_and_adjust_balances(db_session):
    """Test updating a Gider (expense) to a Transfer with correct balance adjustment.
    
    Scenario:
    1. Create s=500, d=100
    2. Create Gider(50): s=450, d=100
    3. Convert Gider to Transfer(50) with hedef_hesap_id=d.id:
       - Revert Gider(50): s=500 (add back 50 removed by Gider)
       - Apply new Transfer(50): s=450, d=150 (deduct from s, add to d)
    
    Expected flow:
    - Before: s=450 (after initial Gider)
    - Revert Gider as Gelir: s=500 (450 + 50)
    - Apply Transfer as Gider on s: s=450 (500 - 50)
    - Apply Transfer as Gelir on d: d=150 (100 + 50)
    """
    session = db_session
    hesap_ctrl = HesapController()
    finans_ctrl = FinansIslemController()

    s = hesap_ctrl.create({"ad": "HTT1", "tur": "Banka", "bakiye": 500.0}, db=session)
    d = hesap_ctrl.create({"ad": "HTT2", "tur": "Banka", "bakiye": 100.0}, db=session)

    islem = finans_ctrl.create({
        "tur": "Gider",
        "tutar": 50.0,
        "hesap_id": s.id,
        "tarih": datetime(2025, 8, 1)
    }, db=session)

    # Verify after Gider
    s_after_gider = hesap_ctrl.get_by_id(s.id, db=session)
    d_after_gider = hesap_ctrl.get_by_id(d.id, db=session)
    assert abs(s_after_gider.bakiye - 450.0) < 0.001, f"Expected s=450, got {s_after_gider.bakiye}"
    assert abs(d_after_gider.bakiye - 100.0) < 0.001, f"Expected d=100, got {d_after_gider.bakiye}"

    # Convert Gider to Transfer (same amount 50)
    finans_ctrl.update_with_balance_adjustment(
        islem.id, 
        {"tur": "Transfer", "hedef_hesap_id": d.id},  # tutar not provided, should use old tutar (50)
        db=session
    )

    s_final = hesap_ctrl.get_by_id(s.id, db=session)
    d_final = hesap_ctrl.get_by_id(d.id, db=session)

    # After conversion:
    # - Revert Gider: s=500, d=100
    # - Apply new Transfer: s=450, d=150
    assert abs(s_final.bakiye - 450.0) < 0.001, f"Expected s=450, got {s_final.bakiye}"
    assert abs(d_final.bakiye - 150.0) < 0.001, f"Expected d=150, got {d_final.bakiye}"
