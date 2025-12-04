import pytest
from types import SimpleNamespace
from ui.aidat_panel import AidatPanel
from ui.base_panel import BasePanel
from datetime import datetime


def fake_base_init(self, parent, title, colors):
    self.parent = parent
    self.title = title
    self.colors = colors
    self.frame = None


class DummyTree:
    def __init__(self):
        self.rows = []
        self.nodes = {}
        self.selected_items = []
        
    def get_children(self):
        return list(range(len(self.rows)))
        
    def delete(self, item):
        # no-op
        pass
        
    def insert(self, parent, index, values, **kwargs):
        self.rows.append(values)
        
    def tag_configure(self, tag_name, **kwargs):
        # no-op for tags configuration
        pass
        
    def selection(self):
        return self.selected_items
        
    def item(self, item, option=None):
        if option == "values":
            return self.rows[int(item)]
        return {"values": self.rows[int(item)]}


class DummyCombo:
    def __init__(self):
        self.values = []
        self._value = None
    def configure(self, values=None, **kwargs):
        if values is not None:
            self.values = values
    def set(self, val):
        self._value = val
    def get(self):
        return self._value


class DummyEntry:
    def __init__(self, value=""):
        self._value = value
    def get(self):
        return self._value
    def delete(self, start, end):
        self._value = ""


def test_load_aidat_islemleri_populates_tree(monkeypatch):
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {'background':'#fff','surface':'#f7f7f7','primary':'#222','text':'#333','success':'#28a745','error':'#dc3545'}
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_islem_tree = DummyTree()

    # Dummy nested daire/lojman objects
    lojman = SimpleNamespace(ad='Test Lojman')
    blok = SimpleNamespace(ad='A', lojman=lojman)
    daire = SimpleNamespace(id=1, blok=blok, daire_no='101')

    # odeme -> finans -> hesap
    finans_hesap = SimpleNamespace(para_birimi='₺')
    finans_islem = SimpleNamespace(hesap=finans_hesap)
    odeme = SimpleNamespace(finans_islem=finans_islem)

    islem = SimpleNamespace(id=1, daire=daire, yil=2025, ay=1, ay_adi='Ocak', aidat_tutari=100.0, katki_payi=0.0, elektrik=0.0, su=0.0, isinma=0.0, ek_giderler=0.0, toplam_tutar=100.0, odemeler=[odeme], son_odeme_tarihi=datetime.now(), aciklama='test')

    panel.aidat_islem_controller = SimpleNamespace(get_all_with_details=lambda: [islem])
    panel.get_sakin_at_date = lambda daire_id, yil, ay: 'Test Sakin'

    panel.load_aidat_islemleri()

    assert len(panel.aidat_islem_tree.rows) == 1


def test_aidat_islem_list_displays_data(monkeypatch):
    """Test that aidat islem list displays data correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_islem_tree = DummyTree()
    
    # Mock data
    lojman = SimpleNamespace(ad='Test Lojman')
    blok = SimpleNamespace(ad='A', lojman=lojman)
    daire = SimpleNamespace(id=1, blok=blok, daire_no='101')
    
    finans_hesap = SimpleNamespace(para_birimi='₺')
    finans_islem = SimpleNamespace(hesap=finans_hesap)
    odeme = SimpleNamespace(finans_islem=finans_islem)
    
    islem = SimpleNamespace(
        id=1, 
        daire=daire, 
        yil=2025, 
        ay=1, 
        ay_adi='Ocak', 
        aidat_tutari=100.0, 
        katki_payi=10.0, 
        elektrik=20.0, 
        su=15.0, 
        isinma=25.0, 
        ek_giderler=5.0, 
        toplam_tutar=175.0, 
        odemeler=[odeme], 
        son_odeme_tarihi=datetime(2025, 1, 31), 
        aciklama='Test aidat'
    )
    
    panel.aidat_islem_controller = SimpleNamespace(get_all_with_details=lambda: [islem])
    panel.get_sakin_at_date = lambda daire_id, yil, ay: 'Test Sakin'
    
    panel.load_aidat_islemleri()
    
    # Check that data is displayed correctly
    assert len(panel.aidat_islem_tree.rows) == 1
    row = panel.aidat_islem_tree.rows[0]
    assert row[0] == 1  # id
    assert row[1] == 'Test Lojman A-101'  # daire
    assert row[2] == 'Test Sakin'  # sakin
    assert row[3] == 2025  # yil
    assert row[4] == 'Ocak'  # ay
    assert '100.00' in row[5]  # aidat_tutari
    assert '10.00' in row[6]  # katki_payi
    assert '20.00' in row[7]  # elektrik
    assert '15.00' in row[8]  # su
    assert '25.00' in row[9]  # isinma
    assert '5.00' in row[10]  # ek_giderler
    assert '175.00' in row[11]  # toplam
    assert row[12] == 'Test aidat'  # aciklama
    assert row[13] == '31.01.2025'  # son_odeme


def test_create_aidat_islem_opens_modal(monkeypatch):
    """Test that creating new aidat islem opens modal"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock CTkToplevel to track if it's called
    toplevel_created = False
    def mock_toplevel(master):
        nonlocal toplevel_created
        toplevel_created = True
        return SimpleNamespace()
    
    monkeypatch.setattr("customtkinter.CTkToplevel", mock_toplevel)
    
    # Mock CTkFont to prevent Tkinter initialization issues
    font_mock = SimpleNamespace()
    monkeypatch.setattr("customtkinter.CTkFont", lambda **kwargs: font_mock)
    
    # Mock daire loading
    panel.load_daireler = lambda: None
    
    # Mock modal opening
    panel.open_aidat_islem_modal = lambda islem: setattr(panel, 'modal_opened', True)
    
    # Call the method
    panel.open_yeni_aidat_islem_modal()
    
    # Check that modal was opened
    assert hasattr(panel, 'modal_opened')
    assert panel.modal_opened


def test_duzenle_aidat_islem_requires_selection(monkeypatch):
    """Test that editing aidat islem requires selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_islem_tree = DummyTree()
    
    # Mock selection to return empty list
    panel.aidat_islem_tree.selected_items = []
    
    # Mock error handler
    error_shown = False
    def mock_show_error(message, title="Hata"):
        nonlocal error_shown
        error_shown = True
        assert "seçin" in str(message).lower()
    
    panel.show_error = mock_show_error
    
    # Call the method
    panel.duzenle_aidat_islem()
    
    # Check that error was shown
    assert error_shown


def test_duzenle_aidat_islem_opens_modal_for_valid_selection(monkeypatch):
    """Test that duzenle_aidat_islem opens modal for valid selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_islem_tree = DummyTree()
    
    # Mock selection
    panel.aidat_islem_tree.selected_items = [0]
    
    # Mock tree item data
    panel.aidat_islem_tree.rows = [[1, "Test Lojman A-101", "Test Sakin", 2025, "Ocak", "100.00", "10.00", "20.00", "15.00", "25.00", "5.00", "175.00", "Test aidat", "31.01.2025"]]
    
    # Mock aidat_islemleri list
    class MockIslem:
        def __init__(self, id):
            self.id = id
            self.odemeler = []
    
    panel.aidat_islemleri = [MockIslem(1)]
    
    # Mock load_daireler method
    daireler_loaded = False
    def mock_load_daireler():
        nonlocal daireler_loaded
        daireler_loaded = True
    
    panel.load_daireler = mock_load_daireler
    
    # Mock open_aidat_islem_modal method
    modal_opened = False
    def mock_open_aidat_islem_modal(islem):
        nonlocal modal_opened
        modal_opened = True
        assert islem.id == 1
    
    panel.open_aidat_islem_modal = mock_open_aidat_islem_modal
    
    # Call the method
    panel.duzenle_aidat_islem()
    
    # Check that methods were called
    assert daireler_loaded
    assert modal_opened


def test_sil_aidat_islem_requires_selection(monkeypatch):
    """Test that deleting aidat islem requires selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_islem_tree = DummyTree()
    
    # Mock selection to return empty list
    panel.aidat_islem_tree.selected_items = []
    
    # Mock error handler
    error_shown = False
    def mock_show_error(message, title="Hata"):
        nonlocal error_shown
        error_shown = True
        assert "seçin" in str(message).lower()
    
    panel.show_error = mock_show_error
    
    # Call the method
    panel.sil_aidat_islem()
    
    # Check that error was shown
    assert error_shown


def test_sil_aidat_islem_successfully_deletes_item(monkeypatch):
    """Test that sil_aidat_islem successfully deletes an item"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_islem_tree = DummyTree()
    
    # Mock selection
    panel.aidat_islem_tree.selected_items = [0]
    
    # Mock tree item data
    panel.aidat_islem_tree.rows = [[1, "Test Lojman A-101", "Test Sakin", 2025, "Ocak", "100.00", "10.00", "20.00", "15.00", "25.00", "5.00", "175.00", "Test aidat", "31.01.2025"]]
    
    # Mock aidat_islemleri list
    class MockIslem:
        def __init__(self, id):
            self.id = id
            self.odemeler = []
            self.daire = SimpleNamespace(blok=SimpleNamespace(lojman=SimpleNamespace(ad="Test Lojman"), ad="A"), daire_no="101")
            self.ay_adi = "Ocak"
            self.yil = 2025
    
    panel.aidat_islemleri = [MockIslem(1)]
    
    # Mock controller delete method
    controller_called = False
    def mock_delete(islem_id):
        nonlocal controller_called
        controller_called = True
        assert islem_id == 1
    
    panel.aidat_islem_controller = SimpleNamespace(delete=mock_delete)
    
    # Mock load_data method
    load_data_called = False
    def mock_load_data():
        nonlocal load_data_called
        load_data_called = True
    
    panel.load_data = mock_load_data
    
    # Mock show_message
    message_shown = False
    def mock_show_message(message, title="Bilgi"):
        nonlocal message_shown
        message_shown = True
        assert "silindi" in message.lower()
    
    panel.show_message = mock_show_message
    
    # Mock messagebox
    import tkinter.messagebox as mock_msgbox
    monkeypatch.setattr(mock_msgbox, 'askyesno', lambda title, message: True)
    
    # Call the method
    panel.sil_aidat_islem()
    
    # Check that methods were called
    assert controller_called
    assert load_data_called
    assert message_shown


def test_filter_by_daire_works(monkeypatch):
    """Test that filtering by daire works correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_islem_tree = DummyTree()
    
    # Mock filter UI elements - these would normally be created in setup_islem_filtreleme_paneli
    panel.filter_islem_daire_combo = DummyCombo()
    panel.filter_islem_daire_combo.set("Test Lojman A-101")
    panel.filter_islem_yil_combo = DummyCombo()
    panel.filter_islem_yil_combo.set("Tümü")
    panel.filter_islem_ay_combo = DummyCombo()
    panel.filter_islem_ay_combo.set("Tümü")
    
    # Mock data with different daireler
    lojman1 = SimpleNamespace(ad='Test Lojman')
    blok1 = SimpleNamespace(ad='A', lojman=lojman1)
    daire1 = SimpleNamespace(id=1, blok=blok1, daire_no='101')
    
    lojman2 = SimpleNamespace(ad='Diğer Lojman')
    blok2 = SimpleNamespace(ad='B', lojman=lojman2)
    daire2 = SimpleNamespace(id=2, blok=blok2, daire_no='202')
    
    finans_hesap = SimpleNamespace(para_birimi='₺')
    finans_islem = SimpleNamespace(hesap=finans_hesap)
    odeme = SimpleNamespace(finans_islem=finans_islem)
    
    islem1 = SimpleNamespace(
        id=1, 
        daire=daire1, 
        yil=2025, 
        ay=1, 
        ay_adi='Ocak', 
        aidat_tutari=100.0, 
        katki_payi=0.0, 
        elektrik=0.0, 
        su=0.0, 
        isinma=0.0, 
        ek_giderler=0.0, 
        toplam_tutar=100.0, 
        odemeler=[odeme], 
        son_odeme_tarihi=datetime(2025, 1, 31), 
        aciklama='Test aidat 1'
    )
    
    islem2 = SimpleNamespace(
        id=2, 
        daire=daire2, 
        yil=2025, 
        ay=2, 
        ay_adi='Şubat', 
        aidat_tutari=150.0, 
        katki_payi=0.0, 
        elektrik=0.0, 
        su=0.0, 
        isinma=0.0, 
        ek_giderler=0.0, 
        toplam_tutar=150.0, 
        odemeler=[odeme], 
        son_odeme_tarihi=datetime(2025, 2, 28), 
        aciklama='Test aidat 2'
    )
    
    # Store original data
    panel.tum_aidat_islemleri_verisi = [islem1, islem2]
    panel.aidat_islemleri = [islem1, islem2]
    
    panel.get_sakin_at_date = lambda daire_id, yil, ay: 'Test Sakin' if daire_id == 1 else 'Diğer Sakin'
    
    # Apply filter
    panel.uygula_islem_filtreler()
    
    # Check that only one item is displayed (matching the filter)
    assert len(panel.aidat_islem_tree.rows) == 1
    row = panel.aidat_islem_tree.rows[0]
    assert row[1] == 'Test Lojman A-101'  # daire


def test_filter_by_month_year_works(monkeypatch):
    """Test that filtering by month and year works correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_islem_tree = DummyTree()
    
    # Mock filter UI elements - these would normally be created in setup_islem_filtreleme_paneli
    panel.filter_islem_daire_combo = DummyCombo()
    panel.filter_islem_daire_combo.set("Tümü")
    panel.filter_islem_yil_combo = DummyCombo()
    panel.filter_islem_yil_combo.set("2025")
    panel.filter_islem_ay_combo = DummyCombo()
    panel.filter_islem_ay_combo.set("Ocak")
    
    # Mock data with different months/years
    lojman = SimpleNamespace(ad='Test Lojman')
    blok = SimpleNamespace(ad='A', lojman=lojman)
    daire = SimpleNamespace(id=1, blok=blok, daire_no='101')
    
    finans_hesap = SimpleNamespace(para_birimi='₺')
    finans_islem = SimpleNamespace(hesap=finans_hesap)
    odeme = SimpleNamespace(finans_islem=finans_islem)
    
    islem1 = SimpleNamespace(
        id=1, 
        daire=daire, 
        yil=2025, 
        ay=1, 
        ay_adi='Ocak', 
        aidat_tutari=100.0, 
        katki_payi=0.0, 
        elektrik=0.0, 
        su=0.0, 
        isinma=0.0, 
        ek_giderler=0.0, 
        toplam_tutar=100.0, 
        odemeler=[odeme], 
        son_odeme_tarihi=datetime(2025, 1, 31), 
        aciklama='Ocak aidat'
    )
    
    islem2 = SimpleNamespace(
        id=2, 
        daire=daire, 
        yil=2025, 
        ay=2, 
        ay_adi='Şubat', 
        aidat_tutari=150.0, 
        katki_payi=0.0, 
        elektrik=0.0, 
        su=0.0, 
        isinma=0.0, 
        ek_giderler=0.0, 
        toplam_tutar=150.0, 
        odemeler=[odeme], 
        son_odeme_tarihi=datetime(2025, 2, 28), 
        aciklama='Şubat aidat'
    )
    
    # Store original data
    panel.tum_aidat_islemleri_verisi = [islem1, islem2]
    panel.aidat_islemleri = [islem1, islem2]
    
    panel.get_sakin_at_date = lambda daire_id, yil, ay: 'Test Sakin'
    
    # Apply filter
    panel.uygula_islem_filtreler()
    
    # Check that only January 2025 item is displayed
    assert len(panel.aidat_islem_tree.rows) == 1
    row = panel.aidat_islem_tree.rows[0]
    assert row[3] == 2025  # yil
    assert row[4] == 'Ocak'  # ay
    assert row[12] == 'Ocak aidat'  # aciklama


def test_aidat_payment_tracking_displays_correctly(monkeypatch):
    """Test that aidat payment tracking displays correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_odeme_tree = DummyTree()
    
    # Mock data for payments
    lojman = SimpleNamespace(ad='Test Lojman')
    blok = SimpleNamespace(ad='A', lojman=lojman)
    daire = SimpleNamespace(id=1, blok=blok, daire_no='101')
    
    aidat_islem = SimpleNamespace(daire=daire)
    
    finans_hesap = SimpleNamespace(para_birimi='₺')
    finans_islem = SimpleNamespace(hesap=finans_hesap)
    
    # Paid payment
    odeme1 = SimpleNamespace(
        id=1,
        aidat_islem=aidat_islem,
        finans_islem=finans_islem,
        tutar=100.0,
        son_odeme_tarihi=datetime(2025, 1, 31),
        odeme_tarihi=datetime(2025, 1, 25),
        durum='Ödendi',
        odendi=True
    )
    
    # Unpaid payment
    odeme2 = SimpleNamespace(
        id=2,
        aidat_islem=aidat_islem,
        finans_islem=finans_islem,
        tutar=150.0,
        son_odeme_tarihi=datetime(2025, 2, 28),
        odeme_tarihi=None,
        durum='Beklemede',
        odendi=False
    )
    
    panel.aidat_odeme_controller = SimpleNamespace(
        get_odeme_bekleyenler=lambda: [odeme2],
        get_odeme_yapilanlar=lambda: [odeme1]
    )
    
    panel.load_aidat_odemeleri()
    
    # Check that both payments are displayed
    assert len(panel.aidat_odeme_tree.rows) == 2
    
    # Check paid payment
    paid_row = panel.aidat_odeme_tree.rows[0]  # Should be first (sorted by ID desc)
    assert paid_row[0] == 2  # id
    assert paid_row[1] == 'Test Lojman A-101'  # daire
    assert '150.00' in paid_row[2]  # tutar
    assert paid_row[3] == '28.02.2025'  # son_odeme
    assert paid_row[4] == ''  # odeme_tarihi (empty because it's the first in sorted order)
    assert paid_row[5] == 'Beklemede'  # durum
    
    # Check unpaid payment
    unpaid_row = panel.aidat_odeme_tree.rows[1]
    assert unpaid_row[0] == 1  # id
    assert unpaid_row[1] == 'Test Lojman A-101'  # daire
    assert '100.00' in unpaid_row[2]  # tutar
    assert unpaid_row[3] == '31.01.2025'  # son_odeme
    assert unpaid_row[4] == '25.01.2025'  # odeme_tarihi
    assert unpaid_row[5] == 'Ödendi'  # durum


def test_odeme_yap_requires_selection(monkeypatch):
    """Test that odeme_yap requires selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_odeme_tree = DummyTree()
    
    # Mock selection to return empty list
    panel.aidat_odeme_tree.selected_items = []
    
    # Mock error handler
    error_shown = False
    def mock_show_error(message, title="Hata"):
        nonlocal error_shown
        error_shown = True
        assert "seçin" in str(message).lower()
    
    panel.show_error = mock_show_error
    
    # Call the method
    panel.odeme_yap()
    
    # Check that error was shown
    assert error_shown


def test_odeme_iptal_requires_selection(monkeypatch):
    """Test that odeme_iptal requires selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_odeme_tree = DummyTree()
    
    # Mock selection to return empty list
    panel.aidat_odeme_tree.selected_items = []
    
    # Mock error handler
    error_shown = False
    def mock_show_error(message, title="Hata"):
        nonlocal error_shown
        error_shown = True
        assert "seçin" in str(message).lower()
    
    panel.show_error = mock_show_error
    
    # Call the method
    panel.odeme_iptal()
    
    # Check that error was shown
    assert error_shown


def test_odeme_iptal_successfully_cancels_payment(monkeypatch):
    """Test that odeme_iptal successfully cancels a payment"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_odeme_tree = DummyTree()
    
    # Mock selection
    panel.aidat_odeme_tree.selected_items = [0]
    
    # Mock tree item data
    panel.aidat_odeme_tree.rows = [[1, "Test Daire", "100.00", "31.01.2025", "25.01.2025", "Ödendi"]]
    
    # Mock aidat_odemeleri list
    class MockOdeme:
        def __init__(self, id, odendi=True):
            self.id = id
            self.odendi = odendi
    
    panel.aidat_odemeleri = [MockOdeme(1, True)]
    
    # Mock controller method
    controller_called = False
    def mock_odeme_iptal(odeme_id):
        nonlocal controller_called
        controller_called = True
        assert odeme_id == 1
    
    panel.aidat_odeme_controller = SimpleNamespace(odeme_iptal=mock_odeme_iptal)
    
    # Mock load_data method
    load_data_called = False
    def mock_load_data():
        nonlocal load_data_called
        load_data_called = True
    
    panel.load_data = mock_load_data
    
    # Mock show_message
    message_shown = False
    def mock_show_message(message, title="Bilgi"):
        nonlocal message_shown
        message_shown = True
        assert "iptal" in message.lower()
    
    panel.show_message = mock_show_message
    
    # Call the method
    panel.odeme_iptal()
    
    # Check that controller method was called
    assert controller_called
    assert load_data_called
    assert message_shown


def test_temizle_islem_filtreler_clears_filters(monkeypatch):
    """Test that temizle_islem_filtreler clears all filters"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock filter UI elements
    panel.filter_islem_daire_combo = DummyCombo()
    panel.filter_islem_daire_combo.set("Test Lojman A-101")
    panel.filter_islem_yil_combo = DummyCombo()
    panel.filter_islem_yil_combo.set("2025")
    panel.filter_islem_ay_combo = DummyCombo()
    panel.filter_islem_ay_combo.set("Ocak")
    
    # Mock uygula_islem_filtreler method to track if it's called
    uygula_called = False
    def mock_uygula_islem_filtreler():
        nonlocal uygula_called
        uygula_called = True
    
    panel.uygula_islem_filtreler = mock_uygula_islem_filtreler
    
    # Call the method
    panel.temizle_islem_filtreler()
    
    # Check that all filters are reset to "Tümü"
    assert panel.filter_islem_daire_combo.get() == "Tümü"
    assert panel.filter_islem_yil_combo.get() == "Tümü"
    assert panel.filter_islem_ay_combo.get() == "Tümü"
    
    # Check that uygula_islem_filtreler is called
    assert uygula_called


def test_get_sakin_at_date_returns_correct_name(monkeypatch):
    """Test that get_sakin_at_date returns correct sakin name"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock database session and query
    class MockSakin:
        def __init__(self, tam_ad):
            self.tam_ad = tam_ad
    
    class MockDB:
        def query(self, model):
            return self
            
        def filter(self, *args):
            return self
            
        def order_by(self, *args):
            return self
            
        def first(self):
            return MockSakin("Test Sakin")
            
        def close(self):
            pass
    
    def mock_get_db():
        return MockDB()
    
    # Monkeypatch database access
    import database.config as db_config
    monkeypatch.setattr(db_config, 'get_db', mock_get_db)
    
    # Call the method
    result = panel.get_sakin_at_date(1, 2025, 1)
    
    # Check that correct name is returned
    assert result == "Test Sakin"


def test_load_daireler_calls_controller(monkeypatch):
    """Test that load_daireler calls controller method"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock controller method
    controller_called = False
    def mock_get_all_with_details():
        nonlocal controller_called
        controller_called = True
        return []
    
    panel.daire_controller = SimpleNamespace(get_all_with_details=mock_get_all_with_details)
    
    # Call the method
    panel.load_daireler()
    
    # Check that controller method was called
    assert controller_called


def test_save_aidat_islem_validates_daire_selection(monkeypatch):
    """Test that save_aidat_islem validates daire selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock modal with required methods
    modal = SimpleNamespace(
        winfo_exists=lambda: True,
        destroy=lambda: None
    )
    
    # Mock error handler to catch the ValidationError
    error_caught = False
    def mock_handle_exception(e, parent=None):
        nonlocal error_caught
        error_caught = True
        # Check that it's a ValidationError with the right message
        assert "daire" in str(e).lower()
    
    from ui.error_handler import handle_exception
    monkeypatch.setattr("ui.aidat_panel.handle_exception", mock_handle_exception)
    
    # Also mock the ErrorHandler context manager to just pass through
    class MockErrorHandler:
        def __init__(self, parent=None, show_success_msg=True):
            pass
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            return False  # Don't suppress exceptions
    
    from ui.error_handler import ErrorHandler
    monkeypatch.setattr("ui.aidat_panel.ErrorHandler", MockErrorHandler)
    
    # Call method with invalid daire selection
    try:
        panel.save_aidat_islem(modal, None, "Daire bulunamadı - Önce daire ekleyin", "2025", "Ocak", 
                              "100", "10", "20", "15", "25", "5", "31.01.2025", "Test açıklama")
    except Exception as e:
        # If an exception is raised, it means our validation worked
        error_caught = True
        assert "daire" in str(e).lower()
    
    # Check that error was caught
    assert error_caught


def test_save_aidat_islem_creates_new_item_successfully(monkeypatch):
    """Test that save_aidat_islem creates new item successfully"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock daireler
    class MockDaire:
        def __init__(self, id, daire_no):
            self.id = id
            self.daire_no = daire_no
            self.blok = SimpleNamespace(lojman=SimpleNamespace(ad="Test Lojman"), ad="A")
            self.guncel_aidat = 100
            self.katki_payi = 10
    
    panel.daireler = [MockDaire(1, "101")]
    
    # Mock modal with required methods
    modal = SimpleNamespace(
        winfo_exists=lambda: True,
        destroy=lambda: None
    )
    
    # Mock error handler to prevent actual error handling
    def mock_handle_exception(e, parent=None):
        # Just re-raise the exception so we can test it
        raise e
    
    from ui.error_handler import handle_exception
    monkeypatch.setattr("ui.aidat_panel.handle_exception", mock_handle_exception)
    
    # Also mock the ErrorHandler context manager to just pass through
    class MockErrorHandler:
        def __init__(self, parent=None, show_success_msg=True):
            pass
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            return False  # Don't suppress exceptions
    
    from ui.error_handler import ErrorHandler
    monkeypatch.setattr("ui.aidat_panel.ErrorHandler", MockErrorHandler)
    
    # Mock controller methods
    islem_created = False
    odeme_created = False
    
    def mock_create_islem(data):
        nonlocal islem_created
        islem_created = True
        return SimpleNamespace(id=1)
    
    def mock_create_odeme(data):
        nonlocal odeme_created
        odeme_created = True
        assert data["aidat_islem_id"] == 1
        assert data["tutar"] == 175.0  # 100 + 10 + 20 + 15 + 25 + 5
    
    panel.aidat_islem_controller = SimpleNamespace(create=mock_create_islem)
    panel.aidat_odeme_controller = SimpleNamespace(create=mock_create_odeme)
    
    # Mock load_data method
    load_data_called = False
    def mock_load_data():
        nonlocal load_data_called
        load_data_called = True
    
    panel.load_data = mock_load_data
    
    # Mock show_success
    success_shown = False
    def mock_show_success(parent, title, message):
        nonlocal success_shown
        success_shown = True
        assert "eklendi" in message.lower()
    
    from ui.error_handler import show_success
    monkeypatch.setattr("ui.aidat_panel.show_success", mock_show_success)
    
    # Call method
    panel.save_aidat_islem(modal, None, "Test Lojman A-101", "2025", "Ocak", 
                          "100", "10", "20", "15", "25", "5", "31.01.2025", "Test açıklama")
    
    # Check that methods were called
    assert islem_created
    assert odeme_created
    assert load_data_called
    assert success_shown


def test_save_odeme_gelir_validates_date_format(monkeypatch):
    """Test that save_odeme_gelir validates date format"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock modal
    modal = SimpleNamespace()
    
    # Mock odeme
    odeme = SimpleNamespace()
    
    # Mock error handler to track error message
    error_shown = False
    error_message = ""
    def mock_show_error(parent, title, message):
        nonlocal error_shown, error_message
        error_shown = True
        error_message = message
    
    # Monkeypatch error handler
    from ui.error_handler import show_error
    monkeypatch.setattr("ui.aidat_panel.show_error", mock_show_error)
    
    # Mock controller methods to bypass account validation
    panel.hesap_controller = SimpleNamespace(get_aktif_hesaplar=lambda: [SimpleNamespace(ad="Hesap")])
    
    # Call method with invalid date format
    panel.save_odeme_gelir(modal, odeme, "invalid_date", "Ana Kat", "Alt Kat", "Hesap", "100", "Açıklama")
    
    # Check that error was shown
    assert error_shown
    assert "GG.AA.YYYY" in error_message


def test_save_odeme_gelir_validates_positive_amount(monkeypatch):
    """Test that save_odeme_gelir validates positive amount"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock modal
    modal = SimpleNamespace()
    
    # Mock odeme
    odeme = SimpleNamespace()
    
    # Mock error handler to track error message
    error_shown = False
    error_message = ""
    def mock_show_error(parent, title, message):
        nonlocal error_shown, error_message
        error_shown = True
        error_message = message
    
    # Monkeypatch error handler
    from ui.error_handler import show_error
    monkeypatch.setattr("ui.aidat_panel.show_error", mock_show_error)
    
    # Mock controller methods to bypass account validation
    panel.hesap_controller = SimpleNamespace(get_aktif_hesaplar=lambda: [SimpleNamespace(ad="Hesap")])
    
    # Call method with negative amount
    panel.save_odeme_gelir(modal, odeme, "01.01.2025", "Ana Kat", "Alt Kat", "Hesap", "-100", "Açıklama")
    
    # Check that error was shown
    assert error_shown
    assert "pozitif" in error_message.lower()


def test_save_odeme_gelir_validates_numeric_amount(monkeypatch):
    """Test that save_odeme_gelir validates numeric amount"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock modal
    modal = SimpleNamespace()
    
    # Mock odeme
    odeme = SimpleNamespace()
    
    # Mock error handler to track error message
    error_shown = False
    error_message = ""
    def mock_show_error(parent, title, message):
        nonlocal error_shown, error_message
        error_shown = True
        error_message = message
    
    # Monkeypatch error handler
    from ui.error_handler import show_error
    monkeypatch.setattr("ui.aidat_panel.show_error", mock_show_error)
    
    # Mock controller methods to bypass account validation
    panel.hesap_controller = SimpleNamespace(get_aktif_hesaplar=lambda: [SimpleNamespace(ad="Hesap")])
    
    # Call method with non-numeric amount
    panel.save_odeme_gelir(modal, odeme, "01.01.2025", "Ana Kat", "Alt Kat", "Hesap", "not_a_number", "Açıklama")
    
    # Check that error was shown
    assert error_shown
    assert "sayı" in error_message.lower()


def test_load_data_calls_all_loading_methods(monkeypatch):
    """Test that load_data calls all loading methods"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock loading methods
    aidat_islemleri_loaded = False
    aidat_odemeleri_loaded = False
    daireler_loaded = False
    
    def mock_load_aidat_islemleri():
        nonlocal aidat_islemleri_loaded
        aidat_islemleri_loaded = True
    
    def mock_load_aidat_odemeleri():
        nonlocal aidat_odemeleri_loaded
        aidat_odemeleri_loaded = True
    
    def mock_load_daireler():
        nonlocal daireler_loaded
        daireler_loaded = True
    
    panel.load_aidat_islemleri = mock_load_aidat_islemleri
    panel.load_aidat_odemeleri = mock_load_aidat_odemeleri
    panel.load_daireler = mock_load_daireler
    
    # Call the method
    panel.load_data()
    
    # Check that all loading methods were called
    assert aidat_islemleri_loaded
    assert aidat_odemeleri_loaded
    assert daireler_loaded


def test_setup_ui_creates_tabs_and_widgets(monkeypatch):
    """Test that setup_ui creates tabs and widgets correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock CTkTabview to track tab creation
    class MockTabview:
        def __init__(self, master, **kwargs):
            self.tabs = {}
            self.master = master
            self.kwargs = kwargs
            
        def pack(self, **kwargs):
            pass
            
        def add(self, tab_name):
            self.tabs[tab_name] = f"tab_{tab_name}"
            return f"tab_{tab_name}"
            
        def tab(self, tab_name):
            return self.tabs.get(tab_name, None)
    
    # Mock the CTkTabview
    monkeypatch.setattr("customtkinter.CTkTabview", MockTabview)
    
    # Mock the setup methods to track if they're called
    islem_tab_setup = False
    takip_tab_setup = False
    data_loaded = False
    
    def mock_setup_aidat_islemleri_tab():
        nonlocal islem_tab_setup
        islem_tab_setup = True
    
    def mock_setup_aidat_takip_tab():
        nonlocal takip_tab_setup
        takip_tab_setup = True
        
    def mock_load_data():
        nonlocal data_loaded
        data_loaded = True
    
    panel.setup_aidat_islemleri_tab = mock_setup_aidat_islemleri_tab
    panel.setup_aidat_takip_tab = mock_setup_aidat_takip_tab
    panel.load_data = mock_load_data
    
    # Call setup_ui
    panel.setup_ui()
    
    # Check that tabs were created
    assert hasattr(panel, 'tabview')
    assert "Aidat İşlemleri" in panel.tabview.tabs
    assert "Aidat Takip" in panel.tabview.tabs
    
    # Check that setup methods were called
    assert islem_tab_setup
    assert takip_tab_setup
    assert data_loaded


def test_setup_aidat_islemleri_tab_creates_widgets(monkeypatch):
    """Test that setup_aidat_islemleri_tab creates all required widgets"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock tabview.tab to return a mock tab
    class MockTab:
        def __init__(self):
            # Add required attributes for Tkinter widgets
            self.tk = SimpleNamespace(call=lambda *args: None, createcommand=lambda name, func: None)
            self._last_child_ids = {}
            # Add the _w attribute that Tkinter widgets need
            self._w = '.!mocktab'
            # Add children attribute for Tkinter parent-child relationships
            self.children = {}
    
    panel.tabview = SimpleNamespace()
    panel.tabview.tab = lambda name: MockTab()
    
    # Mock CTkButton, CTkFrame, and other widgets to track creation
    buttons_created = []
    frames_created = []
    trees_created = []
    
    class MockWidget:
        def __init__(self, master, **kwargs):
            self.master = master
            self.kwargs = kwargs
            for key, value in kwargs.items():
                setattr(self, key, value)
            # Add required attributes for Tkinter widgets
            self.tk = getattr(master, 'tk', None) or SimpleNamespace()
            self._last_child_ids = {}
            # Add the _w attribute that Tkinter widgets need
            self._w = str(id(self))
            # Add children attribute for Tkinter parent-child relationships
            self.children = {}
        
        def pack(self, **kwargs):
            pass
            
        def grid(self, **kwargs):
            pass
            
        def grid_rowconfigure(self, row, **kwargs):
            pass
            
        def grid_columnconfigure(self, column, **kwargs):
            pass
            
        def configure(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
                
        def heading(self, column, **kwargs):
            pass
            
        def column(self, column, **kwargs):
            pass
            
        def yview(self, *args):
            pass
            
        def set(self, first, last):
            pass
            
        def bind(self, event, callback):
            pass
            
        def tag_configure(self, tagname, **kwargs):
            pass    
    def mock_ctk_button(master, **kwargs):
        btn = MockWidget(master, **kwargs)
        buttons_created.append(btn)
        return btn
        
    def mock_ctk_frame(master, **kwargs):
        frame = MockWidget(master, **kwargs)
        frames_created.append(frame)
        return frame
        
    def mock_treeview(master, **kwargs):
        tree = MockWidget(master, **kwargs)
        trees_created.append(tree)
        return tree
        
    def mock_scrollbar(master, **kwargs):
        # Simplified mock for Scrollbar that doesn't try to make actual Tkinter calls
        scrollbar = SimpleNamespace()
        scrollbar.pack = lambda **kw: None
        scrollbar.grid = lambda **kw: None
        scrollbar.set = lambda first, last: None
        scrollbar.configure = lambda **kw: None
        return scrollbar
        
    monkeypatch.setattr("customtkinter.CTkButton", mock_ctk_button)
    monkeypatch.setattr("customtkinter.CTkFrame", mock_ctk_frame)
    monkeypatch.setattr("tkinter.ttk.Treeview", mock_treeview)
    monkeypatch.setattr("tkinter.ttk.Scrollbar", mock_scrollbar)
    
    # Mock Menu to prevent Tkinter initialization issues
    class MockMenu:
        def __init__(self, master=None, **kwargs):
            self.master = master
            self.kwargs = kwargs
            # Add required attributes for Tkinter Menu
            self.tk = getattr(master, 'tk', None) or SimpleNamespace(call=lambda *args: None, createcommand=lambda name, func: None)
            self._last_child_ids = {}
            self._w = str(id(self))
        
        def add_command(self, label, command):
            # Just store the command for testing purposes
            pass
        
        def tk_popup(self, x, y):
            pass
        
        def grab_release(self):
            pass
    
    monkeypatch.setattr("tkinter.Menu", MockMenu)
    
    # Mock setup_islem_filtreleme_paneli
    filtreleme_setup = False
    def mock_setup_islem_filtreleme_paneli(parent):
        nonlocal filtreleme_setup
        filtreleme_setup = True
    
    panel.setup_islem_filtreleme_paneli = mock_setup_islem_filtreleme_paneli
    
    # Call the method
    panel.setup_aidat_islemleri_tab()
    
    # Check that required widgets were created
    assert len(buttons_created) > 0
    assert len(frames_created) > 0
    assert len(trees_created) > 0
    
    # Check that the add button was created with correct text
    add_button = next((btn for btn in buttons_created if "Yeni Aidat İşlemi Ekle" in str(btn.text)), None)
    assert add_button is not None
    assert add_button.fg_color == colors["success"]
    
    # Check that treeview has correct columns
    tree = trees_created[0] if trees_created else None
    assert tree is not None
    assert "columns" in tree.__dict__
    assert "id" in tree.columns
    assert "daire" in tree.columns
    assert "sakin" in tree.columns
    
    # Check that context menu was created
    assert hasattr(panel, 'aidat_islem_context_menu')
    
    # Check that filtreleme panel was set up
    assert filtreleme_setup

def test_setup_aidat_takip_tab_creates_widgets(monkeypatch):
    """Test that setup_aidat_takip_tab creates all required widgets"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock tabview.tab to return a mock tab
    class MockTab:
        def __init__(self):
            # Add required attributes for Tkinter widgets
            self.tk = SimpleNamespace(call=lambda *args: None, createcommand=lambda name, func: None)
            self._last_child_ids = {}
            # Add the _w attribute that Tkinter widgets need
            self._w = '.!mocktab'
            # Add children attribute for Tkinter parent-child relationships
            self.children = {}
    
    panel.tabview = SimpleNamespace()
    panel.tabview.tab = lambda name: MockTab()
    
    # Mock CTkFrame and other widgets to track creation
    frames_created = []
    trees_created = []
    
    class MockWidget:
        def __init__(self, master, **kwargs):
            self.master = master
            self.kwargs = kwargs
            for key, value in kwargs.items():
                setattr(self, key, value)
            # Add required attributes for Tkinter widgets
            self.tk = getattr(master, 'tk', None) or SimpleNamespace()
            self._last_child_ids = {}
            # Add the _w attribute that Tkinter widgets need
            self._w = str(id(self))
            # Add children attribute for Tkinter parent-child relationships
            self.children = {}
        
        def pack(self, **kwargs):
            pass
            
        def grid(self, **kwargs):
            pass
            
        def grid_rowconfigure(self, row, **kwargs):
            pass
            
        def grid_columnconfigure(self, column, **kwargs):
            pass
            
        def configure(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
                
        def heading(self, column, **kwargs):
            pass
            
        def column(self, column, **kwargs):
            pass
            
        def yview(self, *args):
            pass
            
        def set(self, first, last):
            pass
            
        def bind(self, event, callback):
            pass
            
        def tag_configure(self, tagname, **kwargs):
            pass
        
        def get_children(self):
            return []
                    
        def get_children(self):
            return []
    
    def mock_ctk_frame(master, **kwargs):
        frame = MockWidget(master, **kwargs)
        frames_created.append(frame)
        return frame
        
    def mock_treeview(master, **kwargs):
        tree = MockWidget(master, **kwargs)
        trees_created.append(tree)
        return tree
    
    def mock_scrollbar(master, **kwargs):
        # Simplified mock for Scrollbar that doesn't try to make actual Tkinter calls
        scrollbar = SimpleNamespace()
        scrollbar.pack = lambda **kw: None
        scrollbar.grid = lambda **kw: None
        scrollbar.set = lambda first, last: None
        scrollbar.configure = lambda **kw: None
        return scrollbar
        
    monkeypatch.setattr("customtkinter.CTkFrame", mock_ctk_frame)
    monkeypatch.setattr("tkinter.ttk.Treeview", mock_treeview)
    monkeypatch.setattr("tkinter.ttk.Scrollbar", mock_scrollbar)
    
    # Mock Menu to prevent Tkinter initialization issues
    class MockMenu:
        def __init__(self, master=None, **kwargs):
            self.master = master
            self.kwargs = kwargs
            # Add required attributes for Tkinter Menu
            self.tk = getattr(master, 'tk', None) or SimpleNamespace(call=lambda *args: None, createcommand=lambda name, func: None)
            self._last_child_ids = {}
            self._w = str(id(self))
        
        def add_command(self, label, command):
            # Just store the command for testing purposes
            pass
        
        def tk_popup(self, x, y):
            pass
        
        def grab_release(self):
            pass
    
    monkeypatch.setattr("tkinter.Menu", MockMenu)
    
    # Mock setup_odeme_filtreleme_paneli
    filtreleme_setup = False
    def mock_setup_odeme_filtreleme_paneli(parent):
        nonlocal filtreleme_setup
        filtreleme_setup = True
    
    panel.setup_odeme_filtreleme_paneli = mock_setup_odeme_filtreleme_paneli
    
    # Call the method
    panel.setup_aidat_takip_tab()
    
    # Check that required widgets were created
    assert len(frames_created) > 0
    assert len(trees_created) > 0
    
    # Check that treeview has correct columns
    tree = trees_created[0] if trees_created else None
    assert tree is not None
    assert "columns" in tree.__dict__
    assert "id" in tree.columns
    assert "daire" in tree.columns
    assert "tutar" in tree.columns
    
    # Check that context menu was created
    assert hasattr(panel, 'aidat_odeme_context_menu')
    
    # Check that filtreleme panel was set up
    assert filtreleme_setup
def test_show_aidat_islem_context_menu_opens_menu(monkeypatch):
    """Test that show_aidat_islem_context_menu opens context menu"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock context menu
    menu_shown = False
    grab_released = False
    
    def mock_tk_popup(x, y):
        nonlocal menu_shown
        menu_shown = True
        assert x == 100
        assert y == 200
    
    def mock_grab_release():
        nonlocal grab_released
        grab_released = True
    
    panel.aidat_islem_context_menu = SimpleNamespace(tk_popup=mock_tk_popup, grab_release=mock_grab_release)
    
    # Mock event
    event = SimpleNamespace(x_root=100, y_root=200)
    
    # Call the method
    panel.show_aidat_islem_context_menu(event)
    
    # Check that menu was shown and grab was released
    assert menu_shown
    assert grab_released


def test_show_aidat_odeme_context_menu_opens_menu(monkeypatch):
    """Test that show_aidat_odeme_context_menu opens context menu"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock context menu
    menu_shown = False
    def mock_tk_popup(x, y):
        nonlocal menu_shown
        menu_shown = True
    
    def mock_grab_release():
        pass
    
    panel.aidat_odeme_context_menu = SimpleNamespace(tk_popup=mock_tk_popup, grab_release=mock_grab_release)
    
    # Mock event
    event = SimpleNamespace(x_root=100, y_root=200)
    
    # Call the method
    panel.show_aidat_odeme_context_menu(event)
    
    # Check that menu was shown
    assert menu_shown


def test_context_menu_operations_work_correctly(monkeypatch):
    """Test that context menu operations work correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock tabview and tabs
    class MockTabview:
        def __init__(self, master, **kwargs):
            self.master = master
            self.kwargs = kwargs
            # Add required attributes for CustomTkinter widgets
            self.tk = getattr(master, 'tk', None) or SimpleNamespace()
            self._last_child_ids = {}
            self.children = {}  # Add missing children attribute
        
        def add(self, name):
            return f"tab_{name}"
            
        def tab(self, name):
            return SimpleNamespace(
                master=None,  # Add missing master attribute
                tk=SimpleNamespace(call=lambda *args: None, createcommand=lambda name, func: None),
                _last_child_ids={},
                _w=f'.!mocktab_{name}',
                children={}  # Add missing children attribute
            )            
        def pack(self, **kwargs):
            pass    
    monkeypatch.setattr("customtkinter.CTkTabview", MockTabview)
    
    # Mock other widgets with pack method
    class MockWidgetWithPack:
        def __init__(self, master=None, **kwargs):
            self.master = master
            self.kwargs = kwargs
            for key, value in kwargs.items():
                setattr(self, key, value)
            # Add required attributes for Tkinter widgets
            self.tk = getattr(master, 'tk', None) or SimpleNamespace()
            self._last_child_ids = {}
            # Add the _w attribute that Tkinter widgets need
            self._w = str(id(self))
            self.children = {}  # Add missing children attribute
                
        def pack(self, **kwargs):
            pass
            
        def grid(self, **kwargs):
            pass
            
        def grid_rowconfigure(self, row, **kwargs):
            pass
            
        def grid_columnconfigure(self, column, **kwargs):
            pass
            
        def configure(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
                
        def heading(self, column, **kwargs):
            pass
            
        def column(self, column, **kwargs):
            pass
            
        def yview(self, *args):
            pass
            
        def set(self, first, last):
            pass
            
        def bind(self, event, callback):
            pass
        
        def tag_configure(self, tagname, **kwargs):
            pass
        
        def get_children(self):
            return []
    monkeypatch.setattr("customtkinter.CTkFrame", MockWidgetWithPack)
    monkeypatch.setattr("customtkinter.CTkButton", MockWidgetWithPack)
    monkeypatch.setattr("tkinter.ttk.Treeview", MockWidgetWithPack)
    monkeypatch.setattr("tkinter.ttk.Scrollbar", lambda master, **kwargs: SimpleNamespace(pack=lambda **kw: None, grid=lambda **kw: None, set=lambda first, last: None, configure=lambda **kw: None))
    
    # Mock CTkFont to prevent Tkinter initialization issues
    font_mock = SimpleNamespace()
    monkeypatch.setattr("customtkinter.CTkFont", lambda **kwargs: font_mock)
    
    # Mock the filtering panel setup to avoid CTkLabel creation issues
    filtreleme_setup = False
    def mock_setup_islem_filtreleme_paneli(parent):
        nonlocal filtreleme_setup
        filtreleme_setup = True
    
    panel.setup_islem_filtreleme_paneli = mock_setup_islem_filtreleme_paneli
    panel.setup_odeme_filtreleme_paneli = lambda parent: None
    
    # Call setup_ui which will create the context menus
    panel.setup_ui()
    
    # Check that the context menus were created and have the expected commands
    # For aidat islem context menu
    assert hasattr(panel, 'aidat_islem_context_menu')
    # We can't easily check the actual commands since they're added during initialization,
    # but we can test that the menu handling methods work correctly
    
    # Test that show_aidat_islem_context_menu can be called without error
    event = SimpleNamespace(x_root=100, y_root=200)
    try:
        panel.show_aidat_islem_context_menu(event)
        menu_works = True
    except:
        menu_works = False
    assert menu_works
    
    # For aidat odeme context menu
    assert hasattr(panel, 'aidat_odeme_context_menu')
    
    # Test that show_aidat_odeme_context_menu can be called without error
    try:
        panel.show_aidat_odeme_context_menu(event)
        menu_works = True
    except:
        menu_works = False
    assert menu_works


def test_filter_odeme_by_daire_works(monkeypatch):
    """Test that filtering aidat odeme by daire works correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_odeme_tree = DummyTree()
    
    # Mock filter UI elements
    panel.filter_odeme_daire_combo = DummyCombo()
    panel.filter_odeme_daire_combo.set("Test Lojman A-101")
    panel.filter_odeme_durum_combo = DummyCombo()
    panel.filter_odeme_durum_combo.set("Tümü")
    panel.filter_odeme_aciklama_entry = DummyEntry("")
    
    # Mock data with different daireler
    class MockOdeme:
        def __init__(self, id, daire_lojman, daire_blok, daire_no, durum="Beklemede"):
            self.id = id
            self.durum = durum
            self.aciklama = None
            
            # Mock aidat_islem and daire structure exactly as in the real implementation
            self.aidat_islem = SimpleNamespace(
                daire=SimpleNamespace(
                    blok=SimpleNamespace(
                        lojman=SimpleNamespace(ad=daire_lojman),
                        ad=daire_blok
                    ),
                    daire_no=daire_no
                )
            )
            
            self.finans_islem = None
            self.tutar = 100.0
            self.son_odeme_tarihi = datetime(2025, 1, 31)
            self.odeme_tarihi = None
            self.odendi = False
    
    # Store original data
    panel.tum_aidat_odemeleri_verisi = [
        MockOdeme(1, "Test Lojman", "A", "101"),  # This should match the filter
        MockOdeme(2, "Diğer Lojman", "B", "202")   # This should not match the filter
    ]
    panel.aidat_odemeleri = panel.tum_aidat_odemeleri_verisi.copy()
    
    # Apply filter
    panel.uygula_odeme_filtreler()
    
    # Check that only one item is displayed (matching the filter)
    assert len(panel.aidat_odeme_tree.rows) == 1


def test_filter_odeme_by_durum_works(monkeypatch):
    """Test that filtering aidat odeme by durum works correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    panel.aidat_odeme_tree = DummyTree()
    
    # Mock filter UI elements
    panel.filter_odeme_daire_combo = DummyCombo()
    panel.filter_odeme_daire_combo.set("Tümü")
    panel.filter_odeme_durum_combo = DummyCombo()
    panel.filter_odeme_durum_combo.set("Ödendi")
    panel.filter_odeme_aciklama_entry = DummyEntry("")
    
    # Mock data with different durumlar
    class MockOdeme:
        def __init__(self, id, durum, daire_info=None):
            self.id = id
            self.durum = durum
            self.aciklama = None
            if daire_info:
                # Mock aidat_islem and daire structure
                parts = daire_info.split()
                if len(parts) >= 2:
                    lojman_ad = parts[0]
                    blok_da = parts[1].split('-')
                    if len(blok_da) >= 2:
                        blok_ad = blok_da[0]
                        daire_no = blok_da[1]
                        self.aidat_islem = SimpleNamespace(
                            daire=SimpleNamespace(
                                blok=SimpleNamespace(
                                    lojman=SimpleNamespace(ad=lojman_ad),
                                    ad=blok_ad
                                ),
                                daire_no=daire_no
                            )
                        )
                    else:
                        self.aidat_islem = None
                else:
                    self.aidat_islem = None
            else:
                self.aidat_islem = None
            self.finans_islem = None
            self.tutar = 100.0
            self.son_odeme_tarihi = datetime(2025, 1, 31)
            self.odeme_tarihi = datetime(2025, 1, 25) if durum == "Ödendi" else None
            self.odendi = (durum == "Ödendi")
    
    # Store original data
    panel.tum_aidat_odemeleri_verisi = [
        MockOdeme(1, "Ödendi", "Test Lojman A-101"),
        MockOdeme(2, "Beklemede", "Test Lojman A-101")
    ]
    panel.aidat_odemeleri = panel.tum_aidat_odemeleri_verisi.copy()
    
    # Apply filter
    panel.uygula_odeme_filtreler()
    
    # Check that only one item is displayed (matching the filter)
    assert len(panel.aidat_odeme_tree.rows) == 1

def test_temizle_odeme_filtreler_clears_filters(monkeypatch):
    """Test that temizle_odeme_filtreler clears all filters"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock filter UI elements
    panel.filter_odeme_daire_combo = DummyCombo()
    panel.filter_odeme_daire_combo.set("Test Lojman A-101")
    panel.filter_odeme_durum_combo = DummyCombo()
    panel.filter_odeme_durum_combo.set("Ödendi")
    panel.filter_odeme_aciklama_entry = DummyEntry("test")
    
    # Mock uygula_odeme_filtreler method to track if it's called
    uygula_called = False
    def mock_uygula_odeme_filtreler():
        nonlocal uygula_called
        uygula_called = True
    
    panel.uygula_odeme_filtreler = mock_uygula_odeme_filtreler
    
    # Call the method
    panel.temizle_odeme_filtreler()
    
    # Check that all filters are reset to "Tümü" or empty
    assert panel.filter_odeme_daire_combo.get() == "Tümü"
    assert panel.filter_odeme_durum_combo.get() == "Tümü"
    # Check that entry is cleared (we can't directly check DummyEntry content)
    
    # Check that uygula_odeme_filtreler is called
    assert uygula_called


def test_sec_belge_updates_ui_state(monkeypatch):
    """Test that sec_belge updates UI state correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Mock filedialog
    test_file_path = "C:/test/document.pdf"
    monkeypatch.setattr("tkinter.filedialog.askopenfilename", lambda **kwargs: test_file_path)
    
    # Mock belge_controller
    panel.belge_controller = SimpleNamespace(dosya_adi_al=lambda path: "document.pdf")
    
    # Mock UI elements
    panel.belge_durumu_label = SimpleNamespace(configure=lambda **kwargs: None)
    panel.belge_sil_btn = SimpleNamespace(configure=lambda **kwargs: None)
    panel.belge_ac_btn = SimpleNamespace(configure=lambda **kwargs: None)
    
    # Call the method
    panel.sec_belge()
    
    # Check that the selected file path is stored
    assert panel.secili_belge_yolu == test_file_path


def test_sil_secili_belge_clears_selection(monkeypatch):
    """Test that sil_secili_belge clears the selected document"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Set initial state
    panel.secili_belge_yolu = "C:/test/document.pdf"
    
    # Mock UI elements
    panel.belge_durumu_label = SimpleNamespace(configure=lambda **kwargs: None)
    panel.belge_sil_btn = SimpleNamespace(configure=lambda **kwargs: None)
    panel.belge_ac_btn = SimpleNamespace(configure=lambda **kwargs: None)
    
    # Call the method
    panel.sil_secili_belge()
    
    # Check that the selected file path is cleared
    assert panel.secili_belge_yolu is None


def test_ac_secili_belge_opens_document(monkeypatch):
    """Test that ac_secili_belge attempts to open the selected document"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AidatPanel(parent=None, colors=colors)
    
    # Set initial state
    test_file_path = "C:/test/document.pdf"
    panel.secili_belge_yolu = test_file_path
    
    # Mock os.path.exists to return True
    import os
    monkeypatch.setattr(os.path, 'exists', lambda path: True)
    
    # Mock os.startfile (Windows) to track if it's called
    startfile_called = False
    startfile_path = ""
    def mock_startfile(path):
        nonlocal startfile_called, startfile_path
        startfile_called = True
        startfile_path = path
    
    monkeypatch.setattr(os, 'startfile', mock_startfile)
    
    # Call the method
    panel.ac_secili_belge()
    
    # Check that startfile was called with the correct path
    assert startfile_called
    assert startfile_path == test_file_path

