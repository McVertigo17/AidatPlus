"""
End-to-end integration tests for Lojman-Sakin data flow.

This module tests the complete workflow from Lojman creation through to Sakin assignment,
ensuring all components work together correctly in a realistic scenario.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from controllers.lojman_controller import LojmanController
from controllers.blok_controller import BlokController
from controllers.daire_controller import DaireController
from controllers.sakin_controller import SakinController
from controllers.aidat_controller import AidatIslemController
from controllers.finans_islem_controller import FinansIslemController
from controllers.hesap_controller import HesapController

from models.base import Lojman, Blok, Daire, Sakin


def test_lojman_to_sakin_complete_flow(db_session):
    """
    Test the complete end-to-end flow:
    Lojman -> Blok -> Daire -> Sakin -> Aidat -> Finans
    
    This test ensures all components integrate correctly.
    """
    session = db_session
    
    # Initialize controllers
    lojman_controller = LojmanController()
    blok_controller = BlokController()
    daire_controller = DaireController()
    sakin_controller = SakinController()
    aidat_controller = AidatIslemController()
    finans_controller = FinansIslemController()
    hesap_controller = HesapController()
    
    # Step 1: Create a Hesap (Account) for financial transactions
    hesap = hesap_controller.create({
        "ad": "Test Hesap",
        "tur": "Banka",
        "bakiye": 10000.0
    }, db=session)
    assert hesap.id is not None
    assert hesap.bakiye == 10000.0
    
    # Step 2: Create Lojman
    lojman = lojman_controller.create({
        "ad": "Test Lojman Istanbul",
        "adres": "Test Adres Istanbul"
    }, db=session)
    assert lojman.id is not None
    assert lojman.ad == "Test Lojman Istanbul"
    
    # Step 3: Create Blok
    blok = blok_controller.create({
        "ad": "Blok A",
        "lojman_id": lojman.id,
        "kat_sayisi": 5
    }, db=session)
    assert blok.id is not None
    assert blok.ad == "Blok A"
    assert blok.lojman_id == lojman.id
    
    # Step 4: Create Daire
    daire = daire_controller.create({
        "daire_no": "101",
        "blok_id": blok.id,
        "kat": 1,
        "kiraya_esas_alan": 80.0,
        "isitilan_alan": 75.0,
        "guncel_aidat": 1500.0,
        "katki_payi": 300.0
    }, db=session)
    assert daire.id is not None
    assert daire.daire_no == "101"
    assert daire.blok_id == blok.id
    
    # Step 5: Create Sakin
    sakin = sakin_controller.create({
        "ad_soyad": "Ahmet Yılmaz",

        "daire_id": daire.id,
        "giris_tarihi": datetime(2025, 1, 15),
        "telefon": "05551234567",
        "email": "ahmet@example.com"
    }, db=session)
    assert sakin.id is not None
    assert sakin.ad_soyad == "Ahmet Yılmaz"
    assert sakin.daire_id == daire.id
    
    # Step 6: Create Aidat Islem
    aidat_islem = aidat_controller.create({
        "daire_id": daire.id,
        "yil": 2025,
        "ay": 1,
        "toplam_tutar": 1500.0,
        "son_odeme_tarihi": datetime(2025, 1, 31),
        "aciklama": "Ocak ayı aidatı"
    }, db=session)
    assert aidat_islem.id is not None
    assert aidat_islem.daire_id == daire.id
    assert aidat_islem.yil == 2025
    assert aidat_islem.ay == 1
    assert aidat_islem.toplam_tutar == 1500.0
    
    # Step 7: Create Finans Islem (payment)
    finans_islem = finans_controller.create({
        "hesap_id": hesap.id,
        "tur": "Gelir",
        "tutar": 1500.0,
        "tarih": datetime(2025, 1, 20),
        "aciklama": "Ocak ayı aidat ödemesi"
    }, db=session)
    assert finans_islem.id is not None
    assert finans_islem.hesap_id == hesap.id
    assert finans_islem.tur == "Gelir"
    assert finans_islem.tutar == 1500.0
    
    # Verify relationships
    # Refresh objects to get updated data
    session.refresh(lojman)
    session.refresh(blok)
    session.refresh(daire)
    session.refresh(sakin)
    session.refresh(hesap)
    
    # Check Lojman relationships
    assert lojman.blok_sayisi == 1
    assert lojman.toplam_daire_sayisi == 1
    
    # Check Blok relationships
    assert len(blok.daireler) == 1
    assert blok.daireler[0].id == daire.id
    
    # Check Daire relationships
    assert daire.blok.id == blok.id
    assert daire.blok.lojman.id == lojman.id
    assert daire.sakini is not None
    assert daire.sakini.id == sakin.id
    
    # Check Sakin relationships
    assert sakin.daire.id == daire.id
    assert sakin.daire.blok.id == blok.id
    assert sakin.daire.blok.lojman.id == lojman.id
    
    # Check Hesap balance update
    assert hesap.bakiye == 11500.0  # Initial 10000 + 1500 payment
    
    # Test data retrieval
    # Get all active sakinler
    aktif_sakinler = sakin_controller.get_aktif_sakinler(db=session)
    assert len(aktif_sakinler) >= 1
    assert any(s.id == sakin.id for s in aktif_sakinler)
    
    # Get daire with sakin info
    daire_with_details = daire_controller.get_by_id(daire.id, db=session)
    assert daire_with_details is not None
    assert daire_with_details.kullanim_durumu == "Dolu"
    
    # Get lojman with all details
    lojman_with_details = lojman_controller.get_by_id(lojman.id, db=session)
    assert lojman_with_details is not None
    assert lojman_with_details.blok_sayisi == 1
    
    print("✅ End-to-end flow test passed successfully!")


def test_lojman_sakin_roundtrip_verification(db_session):
    """
    Test roundtrip verification of Lojman-Sakin relationships.
    
    Ensures that data integrity is maintained throughout the hierarchy.
    """
    session = db_session
    
    # Initialize controllers
    lojman_controller = LojmanController()
    blok_controller = BlokController()
    daire_controller = DaireController()
    sakin_controller = SakinController()
    
    # Create hierarchy
    lojman = lojman_controller.create({
        "ad": "Roundtrip Test Lojman",
        "adres": "Roundtrip Test Adres"
    }, db=session)
    
    blok = blok_controller.create({
        "ad": "Blok B",
        "lojman_id": lojman.id,
        "kat_sayisi": 3
    }, db=session)
    
    daire1 = daire_controller.create({
        "daire_no": "201",
        "blok_id": blok.id,
        "kat": 2,
        "kiraya_esas_alan": 85.0
    }, db=session)
    
    daire2 = daire_controller.create({
        "daire_no": "202",
        "blok_id": blok.id,
        "kat": 2,
        "kiraya_esas_alan": 90.0
    }, db=session)
    
    sakin1 = sakin_controller.create({
        "ad_soyad": "Mehmet Demir",

        "daire_id": daire1.id,
        "giris_tarihi": datetime(2025, 2, 1)
    }, db=session)
    
    sakin2 = sakin_controller.create({
        "ad_soyad": "Ayşe Kaya",

        "daire_id": daire2.id,
        "giris_tarihi": datetime(2025, 2, 5)
    }, db=session)
    
    # Verify roundtrip relationships
    # From Lojman down to Sakin
    retrieved_lojman = lojman_controller.get_by_id(lojman.id, db=session)
    assert len(retrieved_lojman.bloklar) == 1
    assert retrieved_lojman.bloklar[0].id == blok.id
    
    retrieved_blok = blok_controller.get_by_id(blok.id, db=session)
    assert len(retrieved_blok.daireler) == 2
    daire_ids = [d.id for d in retrieved_blok.daireler]
    assert daire1.id in daire_ids
    assert daire2.id in daire_ids
    
    # From Sakin up to Lojman
    retrieved_sakin1 = sakin_controller.get_by_id(sakin1.id, db=session)
    assert retrieved_sakin1.daire.id == daire1.id
    assert retrieved_sakin1.daire.blok.id == blok.id
    assert retrieved_sakin1.daire.blok.lojman.id == lojman.id
    
    retrieved_sakin2 = sakin_controller.get_by_id(sakin2.id, db=session)
    assert retrieved_sakin2.daire.id == daire2.id
    assert retrieved_sakin2.daire.blok.id == blok.id
    assert retrieved_sakin2.daire.blok.lojman.id == lojman.id
    
    # Verify property calculations
    session.refresh(lojman)
    assert lojman.toplam_daire_sayisi == 2
    assert lojman.toplam_kiraya_esas_alan == 175.0  # 85 + 90
    
    print("✅ Roundtrip verification test passed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])