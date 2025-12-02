from controllers.bos_konut_controller import BosKonutController
from datetime import datetime


def test_get_days_in_month():
    """Test get_days_in_month method"""
    controller = BosKonutController()
    
    # Test February in leap year
    days = controller.get_days_in_month(2024, 2)
    assert days == 29
    
    # Test February in non-leap year
    days = controller.get_days_in_month(2023, 2)
    assert days == 28
    
    # Test months with 31 days
    days = controller.get_days_in_month(2023, 1)  # January
    assert days == 31
    
    # Test months with 30 days
    days = controller.get_days_in_month(2023, 4)  # April
    assert days == 30


def test_get_month_start_end():
    """Test get_month_start_end method"""
    controller = BosKonutController()
    
    # Test January 2023
    start, end = controller.get_month_start_end(2023, 1)
    assert start == datetime(2023, 1, 1)
    assert end == datetime(2023, 1, 31)
    
    # Test February 2024 (leap year)
    start, end = controller.get_month_start_end(2024, 2)
    assert start == datetime(2024, 2, 1)
    assert end == datetime(2024, 2, 29)


def test_calculate_empty_housing_costs_empty_daire():
    """Test calculate_empty_housing_costs with empty daire (no residents)"""
    controller = BosKonutController()
    
    # Sample data
    year = 2023
    month = 1
    
    daire_listesi = [
        {'id': 1, 'daire_no': '101', 'bagliBlokId': 1, 'kiraya_esasi_alan': 75.0}
    ]
    
    blok_listesi = [
        {'id': 1, 'blok_adi': 'A Blok', 'bagliLojmanId': 1}
    ]
    
    lojman_listesi = [
        {'id': 1, 'lojman_adi': 'Test Lojmanı'}
    ]
    
    gider_kayitlari = [
        {'islem_tarihi': '2023-01-15', 'tutar': 1000.0},
        {'islem_tarihi': '2023-01-20', 'tutar': 500.0}
    ]
    
    sakin_listesi = []  # No residents
    
    # Calculate costs
    records, total_cost = controller.calculate_empty_housing_costs(
        year, month, daire_listesi, blok_listesi, lojman_listesi, 
        gider_kayitlari, sakin_listesi
    )
    
    # Assertions
    assert len(records) == 1
    record = records[0]
    assert record['daire_no'] == '101'
    assert record['sorumlu_gun_sayisi'] == 31  # All days empty
    assert abs(record['konut_aidat_bedeli'] - 1500.0) < 0.001  # (1000+500) / 1 / 31 * 31
    assert total_cost == record['konut_aidat_bedeli']


def test_calculate_empty_housing_costs_occupied_daire():
    """Test calculate_empty_housing_costs with occupied daire"""
    controller = BosKonutController()
    
    # Sample data
    year = 2023
    month = 1
    
    daire_listesi = [
        {'id': 1, 'daire_no': '101', 'bagliBlokId': 1, 'kiraya_esasi_alan': 75.0}
    ]
    
    blok_listesi = [
        {'id': 1, 'blok_adi': 'A Blok', 'bagliLojmanId': 1}
    ]
    
    lojman_listesi = [
        {'id': 1, 'lojman_adi': 'Test Lojmanı'}
    ]
    
    gider_kayitlari = [
        {'islem_tarihi': '2023-01-15', 'tutar': 3100.0}  # 100 TL per day total
    ]
    
    # Resident occupying the entire month
    sakin_listesi = [
        {
            'daire_id': 1,
            'giris_tarihi': '2023-01-01',
            'cikis_tarihi': None
        }
    ]
    
    # Calculate costs
    records, total_cost = controller.calculate_empty_housing_costs(
        year, month, daire_listesi, blok_listesi, lojman_listesi, 
        gider_kayitlari, sakin_listesi
    )
    
    # Assertions - should be no empty housing costs since occupied all month
    assert len(records) == 0
    assert total_cost == 0.0


def test_calculate_empty_housing_costs_partial_occupancy():
    """Test calculate_empty_housing_costs with partial occupancy"""
    controller = BosKonutController()
    
    # Sample data
    year = 2023
    month = 1  # January has 31 days
    
    daire_listesi = [
        {'id': 1, 'daire_no': '101', 'bagliBlokId': 1, 'kiraya_esasi_alan': 75.0}
    ]
    
    blok_listesi = [
        {'id': 1, 'blok_adi': 'A Blok', 'bagliLojmanId': 1}
    ]
    
    lojman_listesi = [
        {'id': 1, 'lojman_adi': 'Test Lojmanı'}
    ]
    
    gider_kayitlari = [
        {'islem_tarihi': '2023-01-15', 'tutar': 3100.0}  # 100 TL per day total for 31 days
    ]
    
    # Resident occupying only first 15 days
    sakin_listesi = [
        {
            'daire_id': 1,
            'giris_tarihi': '2023-01-01',
            'cikis_tarihi': '2023-01-15'  # Exits on Jan 15 (inclusive)
        }
    ]
    
    # Calculate costs
    records, total_cost = controller.calculate_empty_housing_costs(
        year, month, daire_listesi, blok_listesi, lojman_listesi, 
        gider_kayitlari, sakin_listesi
    )
    
    # Assertions
    assert len(records) == 1
    record = records[0]
    assert record['daire_no'] == '101'
    assert record['sorumlu_gun_sayisi'] == 16  # Days 16-31 are empty (16 days)
    # Cost calculation: (3100 / 1 / 31) * 16 = 100 * 16 = 1600
    assert abs(record['konut_aidat_bedeli'] - 1600.0) < 0.001
    assert total_cost == record['konut_aidat_bedeli']


def test_format_currency():
    """Test format_currency method"""
    controller = BosKonutController()
    
    # Test regular amount
    result = controller.format_currency(1234.56)
    assert result == "₺1.234,56"
    
    # Test whole number
    result = controller.format_currency(1000.0)
    assert result == "₺1.000,00"
    
    # Test small amount
    result = controller.format_currency(0.5)
    assert result == "₺0,50"


def test_format_date():
    """Test format_date method"""
    controller = BosKonutController()
    
    # Test date formatting
    test_date = datetime(2023, 1, 15)
    result = controller.format_date(test_date)
    assert result == "15.01.2023"
    
    # Test another date
    test_date = datetime(2024, 12, 31)
    result = controller.format_date(test_date)
    assert result == "31.12.2024"