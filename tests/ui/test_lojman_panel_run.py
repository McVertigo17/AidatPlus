import pytest
from types import SimpleNamespace
from ui.lojman_panel import LojmanPanel
from ui.base_panel import BasePanel


def fake_base_init(self, parent, title, colors):
    self.parent = parent
    self.title = title
    self.colors = colors
    self.frame = None


class DummyTree:
    def __init__(self):
        self.rows = []
        self.selected_items = []
        self.nodes = {}

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

    def identify_row(self, y):
        # Return a mock row identifier
        return "item1"


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
    def cget(self, attr):
        if attr == "values":
            return self.values
        return None
    def focus(self):
        pass  # Mock focus method


class DummyEntry:
    def __init__(self, value=""):
        self._value = value
    def get(self):
        return self._value
    def delete(self, start, end):
        self._value = ""
    def insert(self, index, value):
        self._value = value
    def focus(self):
        pass  # Mock focus method


class DummyTextBox:
    def __init__(self, value=""):
        self._value = value
    def get(self, start="1.0", end="end"):
        return self._value
    def delete(self, start, end):
        self._value = ""
    def insert(self, index, value):
        self._value = value
    def focus(self):
        pass  # Mock focus method


def test_load_data_populates_trees_and_combos(monkeypatch):
    # Patch BasePanel to avoid actual UI
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)

    # Provide dummy UI widgets
    panel.lojman_tree = DummyTree()
    panel.blok_tree = DummyTree()
    panel.daire_tree = DummyTree()
    panel.blok_lojman_combo = DummyCombo()
    panel.daire_blok_combo = DummyCombo()

    # Provide dummy objects for controllers
    class DummyLojman:
        def __init__(self, id, ad):
            self.id = id
            self.ad = ad
            self.adres = 'Test'
            self.blok_sayisi = 1
            self.toplam_daire_sayisi = 1
            self.toplam_kiraya_esas_alan = 10.0
            self.toplam_isitilan_alan = 10.0

    class DummyBlok:
        def __init__(self, id, ad):
            self.id = id
            self.ad = ad
            self.lojman = DummyLojman(1, 'L1')
            self.kat_sayisi = 3
            self.giris_kapi_no = 1
            self.daire_sayisi = 10
            self.toplam_kiraya_esas_alan = 75.0
            self.toplam_isitilan_alan = 75.0
            self.notlar = ''

    class DummyDaire:
        def __init__(self, id):
            self.id = id
            self.blok = DummyBlok(1, 'A')
            self.daire_no = '101'
            self.kullanim_durumu = 'Konut'
            self.kat = 1
            self.oda_sayisi = 2
            self.kiraya_esas_alan = 75.0
            self.isitilan_alan = 75.0
            self.tahsis_durumu = 'Tahsis'
            self.isinma_tipi = 'Merkezi'
            self.guncel_aidat = 1200.0
            self.katki_payi = 50.0
            self.aciklama = 'Test'

    dummy_l = DummyLojman(1, 'Lojman 1')
    dummy_b = DummyBlok(2, 'A')
    dummy_d = DummyDaire(3)

    panel.lojman_controller = SimpleNamespace(get_all_with_details=lambda: [dummy_l])
    panel.blok_controller = SimpleNamespace(get_all_with_details=lambda: [dummy_b])
    panel.daire_controller = SimpleNamespace(get_all_with_details=lambda: [dummy_d])

    # Run load
    panel.load_data()

    # Assertions
    assert len(panel.lojman_tree.rows) == 1
    assert len(panel.blok_tree.rows) == 1
    assert len(panel.daire_tree.rows) == 1
    assert panel.blok_lojman_combo.values == ['Lojman 1']
    # Fix the assertion - the combo value format is "Lojman Ad - Blok Ad Blok"
    assert panel.daire_blok_combo.values == ['L1 - A Blok']


def test_load_lojmanlar_populates_tree(monkeypatch):
    """Test that load_lojmanlar populates the lojman tree correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.lojman_tree = DummyTree()

    # Mock data
    class MockLojman:
        def __init__(self, id, ad, adres, blok_sayisi, toplam_daire_sayisi, toplam_kiraya_esas_alan, toplam_isitilan_alan):
            self.id = id
            self.ad = ad
            self.adres = adres
            self.blok_sayisi = blok_sayisi
            self.toplam_daire_sayisi = toplam_daire_sayisi
            self.toplam_kiraya_esas_alan = toplam_kiraya_esas_alan
            self.toplam_isitilan_alan = toplam_isitilan_alan

    mock_lojman = MockLojman(1, "Test Lojman", "Test Address", 2, 10, 100.0, 90.0)
    
    panel.lojman_controller = SimpleNamespace(get_all_with_details=lambda: [mock_lojman])

    # Call the method
    panel.load_lojmanlar()

    # Check that data is loaded correctly
    assert len(panel.lojman_tree.rows) == 1
    row = panel.lojman_tree.rows[0]
    assert row[0] == 1  # id
    assert row[1] == "Test Lojman"  # ad
    assert row[2] == "Test Address"  # adres
    assert row[3] == 2  # blok_sayisi
    assert row[4] == 10  # toplam_daire_sayisi
    assert "100.0" in row[5]  # toplam_kiraya_esas_alan
    assert "90.0" in row[6]  # toplam_isitilan_alan


def test_load_bloklar_populates_tree(monkeypatch):
    """Test that load_bloklar populates the blok tree correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.blok_tree = DummyTree()

    # Mock data
    class MockLojman:
        def __init__(self, ad):
            self.ad = ad

    class MockBlok:
        def __init__(self, id, lojman, ad, kat_sayisi, giris_kapi_no, daire_sayisi, toplam_kiraya_esas_alan, toplam_isitilan_alan, notlar):
            self.id = id
            self.lojman = lojman
            self.ad = ad
            self.kat_sayisi = kat_sayisi
            self.giris_kapi_no = giris_kapi_no
            self.daire_sayisi = daire_sayisi
            self.toplam_kiraya_esas_alan = toplam_kiraya_esas_alan
            self.toplam_isitilan_alan = toplam_isitilan_alan
            self.notlar = notlar

    mock_lojman = MockLojman("Test Lojman")
    mock_blok = MockBlok(1, mock_lojman, "A", 5, 1, 20, 150.0, 140.0, "Test notes")
    
    panel.blok_controller = SimpleNamespace(get_all_with_details=lambda: [mock_blok])

    # Call the method
    panel.load_bloklar()

    # Check that data is loaded correctly
    assert len(panel.blok_tree.rows) == 1
    row = panel.blok_tree.rows[0]
    assert row[0] == 1  # id
    assert row[1] == "Test Lojman"  # lojman
    assert row[2] == "A"  # ad
    assert row[3] == 5  # kat_sayisi
    assert row[4] == 1  # giris_kapi_no
    assert row[5] == 20  # daire_sayisi
    assert "150.0" in row[6]  # toplam_kiraya_esas_alan
    assert "140.0" in row[7]  # toplam_isitilan_alan
    assert row[8] == "Test notes"  # notlar


def test_load_daireler_populates_tree(monkeypatch):
    """Test that load_daireler populates the daire tree correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.daire_tree = DummyTree()

    # Mock data
    class MockLojman:
        def __init__(self, ad):
            self.ad = ad

    class MockBlok:
        def __init__(self, lojman, ad):
            self.lojman = lojman
            self.ad = ad

    class MockDaire:
        def __init__(self, id, blok, daire_no, kullanim_durumu, kat, oda_sayisi, kiraya_esas_alan, isitilan_alan, tahsis_durumu, isinma_tipi, guncel_aidat, katki_payi, aciklama):
            self.id = id
            self.blok = blok
            self.daire_no = daire_no
            self.kullanim_durumu = kullanim_durumu
            self.kat = kat
            self.oda_sayisi = oda_sayisi
            self.kiraya_esas_alan = kiraya_esas_alan
            self.isitilan_alan = isitilan_alan
            self.tahsis_durumu = tahsis_durumu
            self.isinma_tipi = isinma_tipi
            self.guncel_aidat = guncel_aidat
            self.katki_payi = katki_payi
            self.aciklama = aciklama

    mock_lojman = MockLojman("Test Lojman")
    mock_blok = MockBlok(mock_lojman, "A")
    mock_daire = MockDaire(1, mock_blok, "101", "Konut", 2, 3, 80.0, 75.0, "Tahsis", "Merkezi Isıtma", 1500.0, 200.0, "Test açıklama")
    
    panel.daire_controller = SimpleNamespace(get_all_with_details=lambda: [mock_daire])
    panel.convert_room_count_to_display = lambda count: f"{count}+1"

    # Call the method
    panel.load_daireler()

    # Check that data is loaded correctly
    assert len(panel.daire_tree.rows) == 1
    row = panel.daire_tree.rows[0]
    assert row[0] == 1  # id
    assert row[1] == "Test Lojman"  # lojman
    assert row[2] == "A"  # blok
    assert row[3] == "101"  # daire_no
    assert row[4] == "Konut"  # kullanim_durumu
    assert row[5] == 2  # kat
    assert row[6] == "3+1"  # oda_sayisi
    assert "80.0" in row[7]  # kiraya_esas_alan
    assert "75.0" in row[8]  # isitilan_alan
    assert row[9] == "Tahsis"  # tahsis_durumu
    assert row[10] == "Merkezi Isıtma"  # isinma_tipi
    assert "1500.00" in row[11]  # guncel_aidat
    assert "200.00" in row[12]  # katki_payi
    assert row[13] == "Test açıklama"  # aciklama


def test_update_lojman_combo_populates_values(monkeypatch):
    """Test that update_lojman_combo populates combo box values correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.blok_lojman_combo = DummyCombo()

    # Mock data
    class MockLojman:
        def __init__(self, ad):
            self.ad = ad

    mock_lojman1 = MockLojman("Lojman 1")
    mock_lojman2 = MockLojman("Lojman 2")
    
    panel.lojmanlar = [mock_lojman1, mock_lojman2]

    # Call the method
    panel.update_lojman_combo()

    # Check that combo is populated correctly
    assert panel.blok_lojman_combo.values == ["Lojman 1", "Lojman 2"]
    assert panel.blok_lojman_combo.get() == "Lojman 1"


def test_update_blok_combo_populates_values(monkeypatch):
    """Test that update_blok_combo populates combo box values correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.daire_blok_combo = DummyCombo()

    # Mock data
    class MockLojman:
        def __init__(self, ad):
            self.ad = ad

    class MockBlok:
        def __init__(self, lojman, ad):
            self.lojman = lojman
            self.ad = ad

    mock_lojman = MockLojman("Test Lojman")
    mock_blok1 = MockBlok(mock_lojman, "A")
    mock_blok2 = MockBlok(mock_lojman, "B")
    
    panel.bloklar = [mock_blok1, mock_blok2]

    # Call the method
    panel.update_blok_combo()

    # Check that combo is populated correctly
    expected_values = ["Test Lojman - A Blok", "Test Lojman - B Blok"]
    assert panel.daire_blok_combo.values == expected_values
    assert panel.daire_blok_combo.get() == "Test Lojman - A Blok"


def test_add_lojman_validates_empty_name(monkeypatch):
    """Test that add_lojman shows error for empty name"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements
    panel.lojman_name_entry = DummyEntry("")  # Empty name
    panel.lojman_adres_textbox = DummyTextBox("Test address")

    # Mock show_error
    error_shown = False
    def mock_show_error(parent=None, title="", message=""):
        nonlocal error_shown
        error_shown = True
        assert "Lojman Adı" in message

    # Monkeypatch the show_error function in the error_handler module
    import ui.error_handler
    monkeypatch.setattr(ui.error_handler, 'show_error', mock_show_error)

    # Call the method
    panel.add_lojman()

    # Check that error was shown
    assert error_shown


def test_add_lojman_validates_input_and_creates_lojman(monkeypatch):
    """Test that add_lojman validates input and creates a new lojman"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements
    panel.lojman_name_entry = DummyEntry("Test Lojman")
    panel.lojman_adres_textbox = DummyTextBox("Test Address")

    # Mock controller method
    lojman_created = False
    def mock_create_lojman(data):
        nonlocal lojman_created
        lojman_created = True
        assert data["ad"] == "Test Lojman"
        assert data["adres"] == "Test Address"
        return SimpleNamespace(id=1, ad="Test Lojman")

    panel.lojman_controller = SimpleNamespace(create=mock_create_lojman)

    # Mock load_data method
    load_data_called = False
    def mock_load_data():
        nonlocal load_data_called
        load_data_called = True

    panel.load_data = mock_load_data

    # Mock show_message
    message_shown = False
    def mock_show_message(message):
        nonlocal message_shown
        message_shown = True
        assert "Test Lojman" in message

    panel.show_message = mock_show_message

    # Call the method
    panel.add_lojman()

    # Check that methods were called
    assert lojman_created
    assert load_data_called
    assert message_shown

    # Check that form fields were cleared
    assert panel.lojman_name_entry.get() == ""
    assert panel.lojman_adres_textbox.get("1.0", "end") == ""


def test_add_lojman_shows_error_for_empty_name(monkeypatch):
    """Test that add_lojman shows error for empty lojman name"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements with empty name
    panel.lojman_name_entry = DummyEntry("")
    panel.lojman_adres_textbox = DummyTextBox("Test Address")

    # Mock show_error
    error_shown = False
    def mock_show_error(parent=None, title="", message=""):
        nonlocal error_shown
        error_shown = True
        assert "Lojman Adı" in message

    # Monkeypatch the show_error function in the error_handler module
    import ui.error_handler
    monkeypatch.setattr(ui.error_handler, 'show_error', mock_show_error)

    # Call the method
    panel.add_lojman()

    # Check that error was shown
    assert error_shown


def test_edit_lojman_requires_selection(monkeypatch):
    """Test that edit_lojman requires selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.lojman_tree = DummyTree()
    
    # Mock selection to return empty list
    panel.lojman_tree.selected_items = []

    # Mock show_error
    error_shown = False
    def mock_show_error(message):
        nonlocal error_shown
        error_shown = True
        assert "seçin" in message.lower()

    panel.show_error = mock_show_error

    # Call the method
    panel.edit_lojman()

    # Check that error was shown
    assert error_shown


def test_edit_lojman_opens_modal_for_valid_selection(monkeypatch):
    """Test that edit_lojman opens modal for valid selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.lojman_tree = DummyTree()
    
    # Mock selection
    panel.lojman_tree.selected_items = ["0"]
    
    # Mock tree item data
    panel.lojman_tree.rows = [["1", "Test Lojman", "Test Address", "2", "10", "100.0", "90.0"]]

    # Mock controller method
    controller_called = False
    def mock_get_by_id(lojman_id):
        nonlocal controller_called
        controller_called = True
        assert lojman_id == 1
        return SimpleNamespace(id=1, ad="Test Lojman", adres="Test Address")

    panel.lojman_controller = SimpleNamespace(get_by_id=mock_get_by_id)

    # Mock modal opening
    modal_opened = False
    def mock_show_edit_lojman_modal(lojman):
        nonlocal modal_opened
        modal_opened = True
        assert lojman.id == 1
        assert lojman.ad == "Test Lojman"

    panel.show_edit_lojman_modal = mock_show_edit_lojman_modal

    # Call the method
    panel.edit_lojman()

    # Check that methods were called
    assert controller_called
    assert modal_opened


def test_delete_lojman_requires_selection(monkeypatch):
    """Test that delete_lojman requires selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.lojman_tree = DummyTree()
    
    # Mock selection to return empty list
    panel.lojman_tree.selected_items = []

    # Mock show_error
    error_shown = False
    def mock_show_error(message):
        nonlocal error_shown
        error_shown = True
        assert "seçin" in message.lower()

    panel.show_error = mock_show_error

    # Call the method
    panel.delete_lojman()

    # Check that error was shown
    assert error_shown


def test_delete_lojman_successfully_deletes_item(monkeypatch):
    """Test that delete_lojman successfully deletes an item"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.lojman_tree = DummyTree()
    
    # Mock selection
    panel.lojman_tree.selected_items = ["0"]
    
    # Mock tree item data
    panel.lojman_tree.rows = [["1", "Test Lojman", "Test Address", "2", "10", "100.0", "90.0"]]

    # Mock messagebox
    import tkinter.messagebox as mock_msgbox
    monkeypatch.setattr(mock_msgbox, 'askyesno', lambda title, message: True)

    # Mock controller method
    controller_called = False
    def mock_delete_lojman(lojman_id):
        nonlocal controller_called
        controller_called = True
        assert lojman_id == 1
        return True

    panel.lojman_controller = SimpleNamespace(delete=mock_delete_lojman)

    # Mock load_data method
    load_data_called = False
    def mock_load_data():
        nonlocal load_data_called
        load_data_called = True

    panel.load_data = mock_load_data

    # Mock show_message
    message_shown = False
    def mock_show_message(message):
        nonlocal message_shown
        message_shown = True
        assert "silindi" in message.lower()

    panel.show_message = mock_show_message

    # Call the method
    panel.delete_lojman()

    # Check that methods were called
    assert controller_called
    assert load_data_called
    assert message_shown


def test_add_daire_validates_input_and_creates_daire(monkeypatch):
    """Test that add_daire validates input and creates a new daire"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements
    panel.daire_blok_combo = DummyCombo()
    panel.daire_blok_combo.set("Test Lojman - A Blok")
    panel.daire_no_entry = DummyEntry("101")
    panel.daire_oda_combo = DummyCombo()
    panel.daire_oda_combo.set("3+1")
    panel.daire_kat_entry = DummyEntry("2")
    panel.daire_kiraya_entry = DummyEntry("80.5")
    panel.daire_isitilan_entry = DummyEntry("75.0")
    panel.daire_tahsis_combo = DummyCombo()
    panel.daire_tahsis_combo.set("Boş")
    panel.daire_isinma_combo = DummyCombo()
    panel.daire_isinma_combo.set("Merkezi Isıtma")
    panel.daire_aidat_entry = DummyEntry("1500.00")
    panel.daire_katki_entry = DummyEntry("200.00")
    panel.daire_aciklama_textbox = DummyTextBox("Test açıklama")

    # Mock lojman controller method
    lojman_found = False
    def mock_get_by_ad(lojman_ad):
        nonlocal lojman_found
        lojman_found = True
        assert lojman_ad == "Test Lojman"
        return SimpleNamespace(id=1, ad="Test Lojman")

    panel.lojman_controller = SimpleNamespace(get_by_ad=mock_get_by_ad)

    # Mock blok controller method
    blok_found = False
    def mock_get_by_ad_and_lojman(blok_ad, lojman_id):
        nonlocal blok_found
        blok_found = True
        assert blok_ad == "A"
        assert lojman_id == 1
        return SimpleNamespace(id=1, ad="A")

    panel.blok_controller = SimpleNamespace(get_by_ad_and_lojman=mock_get_by_ad_and_lojman)

    # Mock daire controller method
    daire_created = False
    def mock_create_daire(data):
        nonlocal daire_created
        daire_created = True
        assert data["blok_id"] == 1
        assert data["daire_no"] == "101"
        assert data["oda_sayisi"] == 3
        assert data["kat"] == 2
        assert data["kiraya_esas_alan"] == 80.5
        assert data["isitilan_alan"] == 75.0
        assert data["tahsis_durumu"] == "Boş"
        assert data["isinma_tipi"] == "Merkezi Isıtma"
        assert data["guncel_aidat"] == 1500.0
        assert data["katki_payi"] == 200.0
        assert data["aciklama"] == "Test açıklama"
        return SimpleNamespace(id=1, daire_no="101")

    panel.daire_controller = SimpleNamespace(create=mock_create_daire)

    # Mock load_data method
    load_data_called = False
    def mock_load_data():
        nonlocal load_data_called
        load_data_called = True

    panel.load_data = mock_load_data

    # Mock show_message
    message_shown = False
    def mock_show_message(message):
        nonlocal message_shown
        message_shown = True
        assert "101" in message

    panel.show_message = mock_show_message

    # Call the method
    panel.add_daire()

    # Check that methods were called
    assert lojman_found
    assert blok_found
    assert daire_created
    assert load_data_called
    assert message_shown

    # Check that form fields were cleared
    assert panel.daire_no_entry.get() == ""
    assert panel.daire_kat_entry.get() == ""
    assert panel.daire_kiraya_entry.get() == ""
    assert panel.daire_isitilan_entry.get() == ""
    assert panel.daire_aidat_entry.get() == ""
    assert panel.daire_katki_entry.get() == ""
    assert panel.daire_aciklama_textbox.get("1.0", "end") == ""


def test_show_lojman_context_menu_opens_menu(monkeypatch):
    """Test that show_lojman_context_menu opens context menu when clicking on a row"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements
    panel.lojman_tree = DummyTree()
    
    # Mock context menu
    menu_posted = False
    def mock_menu_post(x, y):
        nonlocal menu_posted
        menu_posted = True
    
    panel.lojman_context_menu = SimpleNamespace(post=mock_menu_post)
    
    # Mock identify_row to return a valid item
    panel.lojman_tree.identify_row = lambda y: "item1"
    
    # Mock selection_set
    panel.lojman_tree.selection_set = lambda item: None
    
    # Create a mock event
    mock_event = SimpleNamespace(y=10, x_root=100, y_root=200)
    
    # Call the method
    panel.show_lojman_context_menu(mock_event)
    
    # Check that menu was posted
    assert menu_posted


def test_show_blok_context_menu_opens_menu(monkeypatch):
    """Test that show_blok_context_menu opens context menu when clicking on a row"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements
    panel.blok_tree = DummyTree()
    
    # Mock context menu
    menu_posted = False
    def mock_menu_post(x, y):
        nonlocal menu_posted
        menu_posted = True
    
    panel.blok_context_menu = SimpleNamespace(post=mock_menu_post)
    
    # Mock identify_row to return a valid item
    panel.blok_tree.identify_row = lambda y: "item1"
    
    # Mock selection_set
    panel.blok_tree.selection_set = lambda item: None
    
    # Create a mock event
    mock_event = SimpleNamespace(y=10, x_root=100, y_root=200)
    
    # Call the method
    panel.show_blok_context_menu(mock_event)
    
    # Check that menu was posted
    assert menu_posted


def test_show_daire_context_menu_opens_menu(monkeypatch):
    """Test that show_daire_context_menu opens context menu when clicking on a row"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements
    panel.daire_tree = DummyTree()
    
    # Mock context menu
    menu_posted = False
    def mock_menu_post(x, y):
        nonlocal menu_posted
        menu_posted = True
    
    panel.daire_context_menu = SimpleNamespace(post=mock_menu_post)
    
    # Mock identify_row to return a valid item
    panel.daire_tree.identify_row = lambda y: "item1"
    
    # Mock selection_set
    panel.daire_tree.selection_set = lambda item: None
    
    # Create a mock event
    mock_event = SimpleNamespace(y=10, x_root=100, y_root=200)
    
    # Call the method
    panel.show_daire_context_menu(mock_event)
    
    # Check that menu was posted
    assert menu_posted


def test_add_daire_shows_error_for_empty_blok(monkeypatch):
    """Test that add_daire shows error for empty blok selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements with empty blok
    panel.daire_blok_combo = DummyCombo()
    panel.daire_blok_combo.set("")
    panel.daire_no_entry = DummyEntry("101")
    panel.daire_oda_combo = DummyCombo()
    panel.daire_oda_combo.set("3+1")
    panel.daire_kat_entry = DummyEntry("2")
    panel.daire_kiraya_entry = DummyEntry("80.5")
    panel.daire_isitilan_entry = DummyEntry("75.0")
    panel.daire_tahsis_combo = DummyCombo()
    panel.daire_tahsis_combo.set("Boş")
    panel.daire_isinma_combo = DummyCombo()
    panel.daire_isinma_combo.set("Merkezi Isıtma")
    panel.daire_aidat_entry = DummyEntry("1500.00")
    panel.daire_katki_entry = DummyEntry("200.00")
    panel.daire_aciklama_textbox = DummyTextBox("Test açıklama")

    # Mock show_error
    error_shown = False
    def mock_show_error(parent=None, title="", message=""):
        nonlocal error_shown
        error_shown = True
        assert "Blok" in message

    # Monkeypatch the show_error function in the error_handler module
    import ui.error_handler
    monkeypatch.setattr(ui.error_handler, 'show_error', mock_show_error)

    # Call the method
    panel.add_daire()

    # Check that error was shown
    assert error_shown


def test_edit_daire_requires_selection(monkeypatch):
    """Test that edit_daire requires selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.daire_tree = DummyTree()
    
    # Mock selection to return empty list
    panel.daire_tree.selected_items = []

    # Mock show_error
    error_shown = False
    def mock_show_error(message):
        nonlocal error_shown
        error_shown = True
        assert "seçin" in message.lower()

    panel.show_error = mock_show_error

    # Call the method
    panel.edit_daire()

    # Check that error was shown
    assert error_shown


def test_edit_daire_opens_modal_for_valid_selection(monkeypatch):
    """Test that edit_daire opens modal for valid selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.daire_tree = DummyTree()
    
    # Mock selection
    panel.daire_tree.selected_items = ["0"]
    
    # Mock tree item data
    panel.daire_tree.rows = [["1", "Test Lojman", "A", "101", "Konut", "2", "3+1", "80.0", "75.0", "Tahsis", "Merkezi Isıtma", "1500.00 ₺", "200.00 ₺", "Test açıklama"]]

    # Mock controller method
    controller_called = False
    def mock_get_by_id(daire_id):
        nonlocal controller_called
        controller_called = True
        assert daire_id == 1
        return SimpleNamespace(id=1, daire_no="101")

    panel.daire_controller = SimpleNamespace(get_by_id=mock_get_by_id)

    # Mock modal opening
    modal_opened = False
    def mock_show_edit_daire_modal(daire):
        nonlocal modal_opened
        modal_opened = True
        assert daire.id == 1
        assert daire.daire_no == "101"

    panel.show_edit_daire_modal = mock_show_edit_daire_modal

    # Call the method
    panel.edit_daire()

    # Check that methods were called
    assert controller_called
    assert modal_opened


def test_delete_daire_requires_selection(monkeypatch):
    """Test that delete_daire requires selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.daire_tree = DummyTree()
    
    # Mock selection to return empty list
    panel.daire_tree.selected_items = []

    # Mock show_error
    error_shown = False
    def mock_show_error(message):
        nonlocal error_shown
        error_shown = True
        assert "seçin" in message.lower()

    panel.show_error = mock_show_error

    # Call the method
    panel.delete_daire()

    # Check that error was shown
    assert error_shown


def test_delete_daire_successfully_deletes_item(monkeypatch):
    """Test that delete_daire successfully deletes an item"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.daire_tree = DummyTree()
    
    # Mock selection
    panel.daire_tree.selected_items = ["0"]
    
    # Mock tree item data
    panel.daire_tree.rows = [["1", "Test Lojman", "A", "101", "Konut", "2", "3+1", "80.0", "75.0", "Tahsis", "Merkezi Isıtma", "1500.00 ₺", "200.00 ₺", "Test açıklama"]]

    # Mock messagebox
    import tkinter.messagebox as mock_msgbox
    monkeypatch.setattr(mock_msgbox, 'askyesno', lambda title, message: True)

    # Mock controller method
    controller_called = False
    def mock_delete_daire(daire_id):
        nonlocal controller_called
        controller_called = True
        assert daire_id == 1
        return True

    panel.daire_controller = SimpleNamespace(delete=mock_delete_daire)

    # Mock load_data method
    load_data_called = False
    def mock_load_data():
        nonlocal load_data_called
        load_data_called = True

    panel.load_data = mock_load_data

    # Mock show_message
    message_shown = False
    def mock_show_message(message):
        nonlocal message_shown
        message_shown = True
        assert "silindi" in message.lower()

    panel.show_message = mock_show_message

    # Call the method
    panel.delete_daire()

    # Check that methods were called
    assert controller_called
    assert load_data_called
    assert message_shown


def test_add_blok_validates_empty_lojman(monkeypatch):
    """Test that add_blok shows error for empty lojman selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements with empty lojman
    panel.blok_lojman_combo = DummyCombo()
    panel.blok_lojman_combo.set("")
    panel.blok_ad_entry = DummyEntry("A")
    panel.blok_kat_entry = DummyEntry("5")
    # Add the missing UI elements
    panel.blok_giris_entry = DummyEntry("1")
    panel.blok_not_textbox = DummyTextBox("Test notes")

    # Mock show_error
    error_shown = False
    def mock_show_error(parent=None, title="", message=""):
        nonlocal error_shown
        error_shown = True
        assert "Lojman" in message

    # Monkeypatch the show_error function in the error_handler module
    import ui.error_handler
    monkeypatch.setattr(ui.error_handler, 'show_error', mock_show_error)

    # Call the method
    panel.add_blok()

    # Check that error was shown
    assert error_shown


def test_add_blok_validates_input_and_creates_blok(monkeypatch):
    """Test that add_blok validates input and creates a new blok"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements
    panel.blok_lojman_combo = DummyCombo()
    panel.blok_lojman_combo.set("Test Lojman")
    panel.blok_ad_entry = DummyEntry("A")
    panel.blok_kat_entry = DummyEntry("5")
    panel.blok_giris_entry = DummyEntry("1")
    panel.blok_not_textbox = DummyTextBox("Test notes")

    # Mock lojman controller method
    lojman_found = False
    def mock_get_by_ad(lojman_ad):
        nonlocal lojman_found
        lojman_found = True
        assert lojman_ad == "Test Lojman"
        return SimpleNamespace(id=1, ad="Test Lojman")

    panel.lojman_controller = SimpleNamespace(get_by_ad=mock_get_by_ad)

    # Mock blok controller method
    blok_created = False
    def mock_create_blok(data):
        nonlocal blok_created
        blok_created = True
        assert data["lojman_id"] == 1
        assert data["ad"] == "A"
        assert data["kat_sayisi"] == 5
        assert data["giris_kapi_no"] == "1"
        assert data["notlar"] == "Test notes"
        return SimpleNamespace(id=1, ad="A")

    panel.blok_controller = SimpleNamespace(create=mock_create_blok)

    # Mock load_data method
    load_data_called = False
    def mock_load_data():
        nonlocal load_data_called
        load_data_called = True

    panel.load_data = mock_load_data

    # Mock show_message
    message_shown = False
    def mock_show_message(message):
        nonlocal message_shown
        message_shown = True
        assert "A" in message

    panel.show_message = mock_show_message

    # Call the method
    panel.add_blok()

    # Check that methods were called
    assert lojman_found
    assert blok_created
    assert load_data_called
    assert message_shown

    # Check that form fields were cleared
    assert panel.blok_ad_entry.get() == ""
    assert panel.blok_kat_entry.get() == ""
    assert panel.blok_giris_entry.get() == ""
    assert panel.blok_not_textbox.get("1.0", "end") == ""


def test_add_blok_shows_error_for_empty_lojman(monkeypatch):
    """Test that add_blok shows error for empty lojman selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    
    # Mock UI elements with empty lojman
    panel.blok_lojman_combo = DummyCombo()
    panel.blok_lojman_combo.set("")
    panel.blok_ad_entry = DummyEntry("A")
    panel.blok_kat_entry = DummyEntry("5")
    # Add the missing UI elements
    panel.blok_giris_entry = DummyEntry("1")
    panel.blok_not_textbox = DummyTextBox("Test notes")

    # Mock show_error
    error_shown = False
    def mock_show_error(parent=None, title="", message=""):
        nonlocal error_shown
        error_shown = True
        assert "Lojman" in message

    # Monkeypatch the show_error function in the error_handler module
    import ui.error_handler
    monkeypatch.setattr(ui.error_handler, 'show_error', mock_show_error)

    # Call the method
    panel.add_blok()

    # Check that error was shown
    assert error_shown


def test_edit_blok_requires_selection(monkeypatch):
    """Test that edit_blok requires selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.blok_tree = DummyTree()
    
    # Mock selection to return empty list
    panel.blok_tree.selected_items = []

    # Mock show_error
    error_shown = False
    def mock_show_error(message):
        nonlocal error_shown
        error_shown = True
        assert "seçin" in message.lower()

    panel.show_error = mock_show_error

    # Call the method
    panel.edit_blok()

    # Check that error was shown
    assert error_shown


def test_edit_blok_opens_modal_for_valid_selection(monkeypatch):
    """Test that edit_blok opens modal for valid selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.blok_tree = DummyTree()
    
    # Mock selection
    panel.blok_tree.selected_items = ["0"]
    
    # Mock tree item data
    panel.blok_tree.rows = [["1", "Test Lojman", "A", "5", "1", "10", "100.0", "90.0", "Notes"]]

    # Mock controller method
    controller_called = False
    def mock_get_by_id(blok_id):
        nonlocal controller_called
        controller_called = True
        assert blok_id == 1
        return SimpleNamespace(id=1, ad="A", kat_sayisi=5, giris_kapi_no=1, notlar="Notes")

    panel.blok_controller = SimpleNamespace(get_by_id=mock_get_by_id)

    # Mock modal opening
    modal_opened = False
    def mock_show_edit_blok_modal(blok):
        nonlocal modal_opened
        modal_opened = True
        assert blok.id == 1
        assert blok.ad == "A"

    panel.show_edit_blok_modal = mock_show_edit_blok_modal

    # Call the method
    panel.edit_blok()

    # Check that methods were called
    assert controller_called
    assert modal_opened


def test_delete_blok_requires_selection(monkeypatch):
    """Test that delete_blok requires selection"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.blok_tree = DummyTree()
    
    # Mock selection to return empty list
    panel.blok_tree.selected_items = []

    # Mock show_error
    error_shown = False
    def mock_show_error(message):
        nonlocal error_shown
        error_shown = True
        assert "seçin" in message.lower()

    panel.show_error = mock_show_error

    # Call the method
    panel.delete_blok()

    # Check that error was shown
    assert error_shown


def test_delete_blok_successfully_deletes_item(monkeypatch):
    """Test that delete_blok successfully deletes an item"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = LojmanPanel(parent=None, colors=colors)
    panel.blok_tree = DummyTree()
    
    # Mock selection
    panel.blok_tree.selected_items = ["0"]
    
    # Mock tree item data
    panel.blok_tree.rows = [["1", "Test Lojman", "A", "5", "1", "10", "100.0", "90.0", "Notes"]]

    # Mock messagebox
    import tkinter.messagebox as mock_msgbox
    monkeypatch.setattr(mock_msgbox, 'askyesno', lambda title, message: True)

    # Mock controller method
    controller_called = False
    def mock_delete_blok(blok_id):
        nonlocal controller_called
        controller_called = True
        assert blok_id == 1
        return True

    panel.blok_controller = SimpleNamespace(delete=mock_delete_blok)

    # Mock load_data method
    load_data_called = False
    def mock_load_data():
        nonlocal load_data_called
        load_data_called = True

    panel.load_data = mock_load_data

    # Mock show_message
    message_shown = False
    def mock_show_message(message):
        nonlocal message_shown
        message_shown = True
        assert "silindi" in message.lower()

    panel.show_message = mock_show_message

    # Call the method
    panel.delete_blok()

    # Check that methods were called
    assert controller_called
    assert load_data_called
    assert message_shown
