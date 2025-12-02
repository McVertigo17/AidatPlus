from types import SimpleNamespace
from ui.sakin_panel import SakinPanel
from ui.base_panel import BasePanel


def fake_base_init(self, parent, title, colors):
    self.parent = parent
    self.title = title
    self.colors = colors
    self.frame = None


class DummyTree:
    def __init__(self):
        self.rows = []

    def get_children(self):
        return list(range(len(self.rows)))

    def delete(self, item):
        # no-op
        pass

    def insert(self, parent, index, values, **kwargs):
        self.rows.append(values)


class DummyCombo:
    def __init__(self):
        self.values = []
    def configure(self, values=None, **kwargs):
        if values is not None:
            self.values = values
    def set(self, value):
        self._value = value
    def get(self):
        return getattr(self, '_value', None)


def test_sakin_panel_initialization(monkeypatch):
    """Test SakinPanel initializes correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'accent': '#e3f2fd',
        'border': '#ddd',
        'text_secondary': '#666'
    }

    panel = SakinPanel(parent=None, colors=colors)

    # Check that controllers are initialized
    assert panel.sakin_controller is not None
    assert panel.daire_controller is not None

    # Check that data lists are initialized
    assert panel.aktif_sakinler == []
    assert panel.pasif_sakinler == []
    assert panel.daireler == []

    # Check that filter variables are initialized
    assert panel.filter_aktif_ad_soyad == ""
    assert panel.filter_aktif_daire == "Tümü"
    assert panel.filter_pasif_ad_soyad == ""
    assert panel.filter_pasif_daire == "Tümü"


def test_load_data_populates_aktif_and_pasif(monkeypatch):
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#fff',
        'surface': '#f7f7f7',
        'primary': '#000',
        'text': '#111',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }

    panel = SakinPanel(parent=None, colors=colors)

    panel.aktif_sakin_tree = DummyTree()
    panel.pasif_sakin_tree = DummyTree()
    panel.filter_aktif_daire_combo = DummyCombo()
    panel.filter_pasif_daire_combo = DummyCombo()

    # Dummy nested objects
    class DummyLojman:
        def __init__(self, ad):
            self.ad = ad

    class DummyBlok:
        def __init__(self, ad, lojman):
            self.ad = ad
            self.lojman = lojman

    class DummyDaire:
        def __init__(self, daire_no):
            self.daire_no = daire_no
            self.blok = DummyBlok('A', DummyLojman('L'))

    class DummySakin:
        def __init__(self, id, ad_soyad, daire=None):
            self.id = id
            self.ad_soyad = ad_soyad
            self.rutbe_unvan = 'Uzman'
            self.daire = daire
            self.telefon = '0555'
            self.email = 'a@b.com'
            self.aile_birey_sayisi = 3
            self.tahsis_tarihi = None
            self.giris_tarihi = None
            self.notlar = ''
            self.cikis_tarihi = None
            self.eski_daire = None

    ds = DummySakin(1, 'Ali Test', DummyDaire('101'))
    ds_pasif = DummySakin(2, 'Veli Test', None)

    panel.sakin_controller = SimpleNamespace(get_aktif_sakinler=lambda: [ds], get_pasif_sakinler=lambda: [ds_pasif])
    panel.daire_controller = SimpleNamespace(get_bos_daireler=lambda: [])

    panel.load_data()

    assert len(panel.aktif_sakin_tree.rows) == 1
    assert len(panel.pasif_sakin_tree.rows) == 1
    assert 'Tümü' in panel.filter_aktif_daire_combo.values
    assert 'Tümü' in panel.filter_pasif_daire_combo.values


def test_setup_ui_creates_components(monkeypatch):
    """Test that setup_ui creates all required UI components"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    # Mock CTk components
    class MockCTkFrame:
        def __init__(self, *args, **kwargs):
            pass
        def pack(self, *args, **kwargs):
            pass
    
    class MockCTkButton:
        def __init__(self, *args, **kwargs):
            pass
        def pack(self, *args, **kwargs):
            pass
            
    class MockCTkTabview:
        def __init__(self, *args, **kwargs):
            self.tabs = {}
        def pack(self, *args, **kwargs):
            pass
        def add(self, name):
            self.tabs[name] = MockCTkFrame(None)
        def tab(self, name):
            return self.tabs.get(name, MockCTkFrame(None))
            
    # Patch CTk classes
    monkeypatch.setattr("ui.sakin_panel.ctk.CTkFrame", MockCTkFrame)
    monkeypatch.setattr("ui.sakin_panel.ctk.CTkButton", MockCTkButton)
    monkeypatch.setattr("ui.sakin_panel.ctk.CTkTabview", MockCTkTabview)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }
    
    panel = SakinPanel(parent=None, colors=colors)
    
    # Mock the tab setup methods
    panel.setup_aktif_sakinler_tab = lambda: None
    panel.setup_arsiv_tab = lambda: None
    panel.load_data = lambda: None
    
    # Call setup_ui
    panel.setup_ui()
    
    # If no exception was raised, the test passes
    assert True


def test_normalize_param_handles_various_inputs(monkeypatch):
    """Test _normalize_param method handles different input types correctly"""
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
    
    panel = SakinPanel(parent=None, colors=colors)
    
    # Test None input
    assert panel._normalize_param(None) == ""
    
    # Test string input
    assert panel._normalize_param("test") == "test"
    assert panel._normalize_param(" test ") == "test"
    
    # Test integer input
    assert panel._normalize_param(123) == "123"
    
    # Test date input (when is_date=True)
    from datetime import datetime
    test_date = datetime(2025, 1, 1)
    assert panel._normalize_param(test_date, is_date=True) == "01.01.2025"


def test_open_yeni_sakin_modal_creates_window(monkeypatch):
    """Test that open_yeni_sakin_modal calls open_sakin_modal with None"""
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
    
    panel = SakinPanel(parent=None, colors=colors)
    
    # Track if open_sakin_modal was called with None
    call_args = []
    def mock_open_sakin_modal(sakin):
        call_args.append(sakin)
    
    panel.open_sakin_modal = mock_open_sakin_modal
    
    # Call the method
    panel.open_yeni_sakin_modal()
    
    # Verify it was called with None
    assert len(call_args) == 1
    assert call_args[0] is None


def test_duzenle_sakin_with_selection(monkeypatch):
    """Test that duzenle_sakin works when there is a selection"""
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
    
    panel = SakinPanel(parent=None, colors=colors)
    
    # Mock tabview to return active tab
    class MockTabview:
        def get(self):
            return "Aktif Sakinler"
    
    panel.tabview = MockTabview()
    
    # Mock tree with selection
    class MockTree:
        def selection(self):
            return ["item1"]  # Return a selection
        
        def item(self, selection, option=None):
            return {'values': [1]}  # Return item values
    
    panel.aktif_sakin_tree = MockTree()
    
    # Mock aktif_sakinler list
    class DummySakin:
        def __init__(self, id):
            self.id = id
    
    panel.aktif_sakinler = [DummySakin(1)]
    
    # Track if open_duzenle_sakin_modal was called
    call_args = []
    def mock_open_duzenle_sakin_modal(sakin):
        call_args.append(sakin)
    
    panel.open_duzenle_sakin_modal = mock_open_duzenle_sakin_modal
    
    # Test with active tab
    panel.duzenle_sakin()
    assert len(call_args) == 1
    assert call_args[0].id == 1


def test_show_error_method_exists(monkeypatch):
    """Test that show_error method exists (inherited from BasePanel)"""
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
    
    panel = SakinPanel(parent=None, colors=colors)
    
    # Check that show_error method exists (would be inherited)
    assert hasattr(panel, 'show_error')


def test_setup_aktif_filtre_paneli_creates_components(monkeypatch):
    """Test that setup_aktif_filtre_paneli creates filter UI components"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    # Mock CTk components
    class MockCTkFrame:
        def __init__(self, *args, **kwargs):
            pass
        def pack(self, *args, **kwargs):
            pass
    
    class MockCTkLabel:
        def __init__(self, *args, **kwargs):
            pass
        def pack(self, *args, **kwargs):
            pass
            
    class MockCTkEntry:
        def __init__(self, *args, **kwargs):
            self.bind_called = False
        def pack(self, *args, **kwargs):
            pass
        def bind(self, event, callback):
            self.bind_called = True
            
    class MockCTkComboBox:
        def __init__(self, *args, **kwargs):
            self.bind_called = False
        def pack(self, *args, **kwargs):
            pass
        def set(self, value):
            pass
        def bind(self, event, callback):
            self.bind_called = True
        def configure(self, *args, **kwargs):
            pass
            
    class MockCTkButton:
        def __init__(self, *args, **kwargs):
            pass
        def pack(self, *args, **kwargs):
            pass
    
    # Patch CTk classes
    monkeypatch.setattr("ui.sakin_panel.ctk.CTkFrame", MockCTkFrame)
    monkeypatch.setattr("ui.sakin_panel.ctk.CTkLabel", MockCTkLabel)
    monkeypatch.setattr("ui.sakin_panel.ctk.CTkEntry", MockCTkEntry)
    monkeypatch.setattr("ui.sakin_panel.ctk.CTkComboBox", MockCTkComboBox)
    monkeypatch.setattr("ui.sakin_panel.ctk.CTkButton", MockCTkButton)
    
    # Mock CTkFont to avoid tkinter initialization issues
    class MockCTkFont:
        def __init__(self, *args, **kwargs):
            pass
    
    monkeypatch.setattr("ui.sakin_panel.ctk.CTkFont", MockCTkFont)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'border': '#ddd'
    }
    
    panel = SakinPanel(parent=None, colors=colors)
    
    # Mock main frame
    mock_main_frame = MockCTkFrame(None)
    
    # Call the method
    panel.setup_aktif_filtre_paneli(mock_main_frame)
    
    # Check that filter entry and combo box were created and bound
    assert hasattr(panel, 'filter_aktif_ad_entry')
    assert hasattr(panel, 'filter_aktif_daire_combo')
    
    # If no exception was raised, the test passes
    assert True


def test_temizle_aktif_filtreler_clears_filters(monkeypatch):
    """Test that temizle_aktif_filtreler clears filter fields and reloads data"""
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
    
    panel = SakinPanel(parent=None, colors=colors)
    
    # Mock filter components
    class MockEntry:
        def __init__(self):
            self.deleted = False
        def delete(self, start, end):
            self.deleted = True
    
    class MockCombo:
        def __init__(self):
            self.value_set = None
        def set(self, value):
            self.value_set = value
    
    panel.filter_aktif_ad_entry = MockEntry()
    panel.filter_aktif_daire_combo = MockCombo()
    
    # Track if load_aktif_sakinler was called
    load_called = []
    def mock_load_aktif_sakinler():
        load_called.append(True)
    
    panel.load_aktif_sakinler = mock_load_aktif_sakinler
    
    # Call the method
    panel.temizle_aktif_filtreler()
    
    # Verify filters were cleared
    assert panel.filter_aktif_ad_entry.deleted
    assert panel.filter_aktif_daire_combo.value_set == "Tümü"
    assert len(load_called) == 1


def test_uygula_aktif_filtreler_applies_filters(monkeypatch):
    """Test that uygula_aktif_filtreler applies filters to the treeview"""
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
    
    panel = SakinPanel(parent=None, colors=colors)
    
    # Mock filter components
    class MockEntry:
        def __init__(self, value):
            self.value = value
        def get(self):
            return self.value
    
    class MockCombo:
        def __init__(self, value):
            self.value = value
        def get(self):
            return self.value
    
    panel.filter_aktif_ad_entry = MockEntry("Ali")
    panel.filter_aktif_daire_combo = MockCombo("Tümü")
    
    # Mock treeview
    panel.aktif_sakin_tree = DummyTree()
    
    # Mock sakin data
    class DummySakin:
        def __init__(self, id, ad_soyad, daire=None):
            self.id = id
            self.ad_soyad = ad_soyad
            self.daire = daire
            self.rutbe_unvan = 'Uzman'
            self.telefon = '0555'
            self.email = 'a@b.com'
            self.aile_birey_sayisi = 3
            self.tahsis_tarihi = None
            self.giris_tarihi = None
            self.notlar = ''
    
    class DummyDaire:
        def __init__(self):
            self.blok = SimpleNamespace(
                lojman=SimpleNamespace(ad="Test Lojman"),
                ad="A"
            )
            self.daire_no = "101"
    
    panel.aktif_sakinler = [
        DummySakin(1, "Ali Test", DummyDaire()),
        DummySakin(2, "Veli Test", DummyDaire())
    ]
    
    # Call the method
    panel.uygula_aktif_filtreler()
    
    # Verify filtering worked (should show 1 row matching "Ali")
    assert len(panel.aktif_sakin_tree.rows) == 1
    assert panel.aktif_sakin_tree.rows[0][1] == "Ali Test"