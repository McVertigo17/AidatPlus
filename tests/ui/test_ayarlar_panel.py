import pytest
from ui.ayarlar_panel import AyarlarPanel
from ui.base_panel import BasePanel
from types import SimpleNamespace
from unittest.mock import MagicMock


def fake_base_init(self, parent, title, colors):
    self.parent = parent
    self.title = title
    self.colors = colors
    self.frame = None


class DummyTree:
    def __init__(self):
        self.rows = []
        self.nodes = {}
        
    def get_children(self, item=''):
        if item == '':
            return list(self.nodes.keys())
        return []
        
    def delete(self, item):
        if item in self.nodes:
            del self.nodes[item]
        if item in self.rows:
            self.rows.remove(item)
            
    def insert(self, parent, index, iid=None, text='', values=None, **kwargs):
        if iid is None:
            iid = len(self.rows)
        self.nodes[iid] = {
            'parent': parent,
            'text': text,
            'values': values or []
        }
        self.rows.append(iid)
        return iid
        
    def item(self, item, option=None, **kwargs):
        if item in self.nodes:
            if option:
                if option == 'text':
                    return self.nodes[item]['text']
                elif option == 'values':
                    return self.nodes[item]['values']
            return self.nodes[item]
        return {}
        
    def tag_configure(self, tag_name, **kwargs):
        pass
        
    def yview_moveto(self, v):
        pass


class DummyButton:
    def __init__(self):
        self.is_packed = False
        
    def pack(self, *args, **kwargs):
        self.is_packed = True


def test_ayarlar_panel_initialization(monkeypatch):
    """Test AyarlarPanel initializes correctly"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'accent': '#e3f2fd'
    }
    
    panel = AyarlarPanel(parent=None, colors=colors)
    
    # Check that controllers are initialized
    assert panel.kategori_controller is not None
    assert panel.backup_controller is not None
    # Note: We don't check for tabview here because it's created during setup_ui which requires a real Tkinter root

def test_load_kategori_listesi_populates_tree(monkeypatch):
    """Test that load_kategori_listesi populates the tree with kategori data"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AyarlarPanel(parent=None, colors=colors)
    panel.kategori_tree = DummyTree()
    
    # Mock controller methods
    class DummyAnaKategori:
        def __init__(self, id, name, tip, aciklama=None):
            self.id = id
            self.name = name
            self.tip = tip
            self.aciklama = aciklama
    
    class DummyAltKategori:
        def __init__(self, id, name, aciklama=None):
            self.id = id
            self.name = name
            self.aciklama = aciklama
    
    # Create mock data
    ana_kategori1 = DummyAnaKategori(1, "Gelir Kategorisi", "gelir", "Açıklama 1")
    ana_kategori2 = DummyAnaKategori(2, "Gider Kategorisi", "gider", "Açıklama 2")
    
    alt_kategori1 = DummyAltKategori(1, "Kira Geliri", "Kira açıklaması")
    alt_kategori2 = DummyAltKategori(2, "Elektrik Faturası", "Elektrik açıklaması")
    
    # Mock controller methods
    panel.kategori_controller = MagicMock()
    panel.kategori_controller.get_ana_kategoriler.return_value = [ana_kategori1, ana_kategori2]
    panel.kategori_controller.get_alt_kategoriler_by_parent.side_effect = lambda parent_id: [alt_kategori1] if parent_id == 1 else [alt_kategori2]
    
    # Load data
    panel.load_kategori_listesi()
    
    # Check that tree has the right number of items
    assert len(panel.kategori_tree.rows) == 4  # 2 ana + 2 alt kategori
    
    # Check that ana kategoriler are added correctly
    ana_items = [item for item in panel.kategori_tree.rows if item.startswith('ana_')]
    assert len(ana_items) == 2
    
    # Check that alt kategoriler are added correctly
    alt_items = [item for item in panel.kategori_tree.rows if item.startswith('alt_')]
    assert len(alt_items) == 2


def test_open_kategori_modal_creates_window(monkeypatch):
    """Test that open_kategori_modal creates a modal window"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AyarlarPanel(parent=None, colors=colors)
    
    # Mock the toplevel window
    toplevel_mock = MagicMock()
    monkeypatch.setattr("customtkinter.CTkToplevel", lambda master: toplevel_mock)
    
    # Mock CTkFont to prevent Tkinter initialization issues
    font_mock = MagicMock()
    monkeypatch.setattr("customtkinter.CTkFont", lambda **kwargs: font_mock)
    
    # Call the method
    panel.open_kategori_modal()
    
    # Check that toplevel was created
    assert toplevel_mock.title.called
    assert toplevel_mock.geometry.called


def test_save_kategori_validates_input(monkeypatch):
    """Test that save_kategori validates input fields"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AyarlarPanel(parent=None, colors=colors)
    
    # Mock UI elements
    panel.ad_entry = MagicMock()
    panel.ad_entry.get.return_value = ""  # Empty name should trigger validation error
    
    panel.aciklama_entry = MagicMock()
    panel.aciklama_entry.get.return_value = ""
    
    panel.kategori_tip_var = MagicMock()
    panel.kategori_tip_var.get.return_value = "ana"
    
    panel.gelir_gider_var = MagicMock()
    panel.gelir_gider_var.get.return_value = "gelir"
    
    # Mock error handler
    error_shown = False
    def mock_show_error(*args, **kwargs):
        nonlocal error_shown
        error_shown = True
    
    monkeypatch.setattr("ui.error_handler.show_error", mock_show_error)
    
    # Mock controller
    panel.kategori_controller = MagicMock()
    
    # Create a mock modal
    modal_mock = MagicMock()
    
    # Call save_kategori
    panel.save_kategori(modal_mock, None)
    
    # Check that error was shown
    assert error_shown


def test_duzenle_kategori_shows_modal(monkeypatch):
    """Test that duzenle_kategori opens modal with selected kategori data"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AyarlarPanel(parent=None, colors=colors)
    panel.kategori_tree = DummyTree()
    
    # Add a test item to the tree
    panel.kategori_tree.insert('', 'end', iid='ana_1', text='Test Kategori', values=['Ana Kategori', '💰 Gelir', '', 'Açıklama'])
    
    # Select the item
    def mock_selection():
        return ['ana_1']
    
    panel.kategori_tree.selection = mock_selection
    
    # Mock item method
    def mock_item(item_id):
        if item_id == 'ana_1':
            return {
                'text': 'Test Kategori',
                'values': ['Ana Kategori', '💰 Gelir', '', 'Açıklama']
            }
        return {}
    
    panel.kategori_tree.item = mock_item
    
    # Mock the modal opening
    modal_opened = False
    def mock_open_kategori_modal(kategori_data=None):
        nonlocal modal_opened
        modal_opened = True
        assert kategori_data is not None
        assert kategori_data['id'] == 1
        assert kategori_data['name'] == 'Test Kategori'
        assert kategori_data['tip'] == 'ana'
        assert kategori_data['gelir_gider'] == 'gelir'
    
    panel.open_kategori_modal = mock_open_kategori_modal
    
    # Call the method
    panel.duzenle_kategori()
    
    # Check that modal was opened
    assert modal_opened


def test_sil_kategori_requires_selection(monkeypatch):
    """Test that sil_kategori shows error when no selection is made"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AyarlarPanel(parent=None, colors=colors)
    panel.kategori_tree = DummyTree()
    
    # Mock selection to return empty list
    def mock_selection():
        return []
    
    panel.kategori_tree.selection = mock_selection
    
    # Mock error handler
    error_shown = False
    def mock_show_error(message, title="Hata"):
        nonlocal error_shown
        error_shown = True
        # Check that the message contains the expected text
        assert "seçin" in str(message).lower()
    
    # Use the correct path for monkeypatching
    monkeypatch.setattr(panel, "show_error", mock_show_error)
    
    # Call the method
    panel.sil_kategori()
    
    # Check that error was shown
    assert error_shown


def test_yedek_al_opens_file_dialog(monkeypatch):
    """Test that yedek_al opens file dialog"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AyarlarPanel(parent=None, colors=colors)
    
    # Mock filedialog
    filedialog_called = False
    def mock_filedialog_asksaveasfilename(**kwargs):
        nonlocal filedialog_called
        filedialog_called = True
        return "/fake/path/backup.xlsx"
    
    monkeypatch.setattr("tkinter.filedialog.asksaveasfilename", mock_filedialog_asksaveasfilename)
    
    # Mock controller
    panel.backup_controller = MagicMock()
    panel.backup_controller.backup_to_excel.return_value = True
    
    # Mock messagebox
    messagebox_called = False
    def mock_show_message(message, title="Bilgi"):
        nonlocal messagebox_called
        messagebox_called = True
    
    panel.show_message = mock_show_message
    
    # Call the method
    panel.yedek_al("excel")
    
    # Check that filedialog was called
    assert filedialog_called
    assert messagebox_called


def test_yedekten_yukle_opens_file_dialog(monkeypatch):
    """Test that yedekten_yukle opens file dialog"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AyarlarPanel(parent=None, colors=colors)
    
    # Mock filedialog
    filedialog_called = False
    def mock_filedialog_askopenfilename(**kwargs):
        nonlocal filedialog_called
        filedialog_called = True
        return "/fake/path/backup.xlsx"
    
    monkeypatch.setattr("tkinter.filedialog.askopenfilename", mock_filedialog_askopenfilename)
    
    # Mock os.path.exists
    monkeypatch.setattr("os.path.exists", lambda x: True)
    
    # Mock messagebox.askyesno
    def mock_ask_yes_no(message, title="Onay"):
        return True  # Simulate user clicking "Yes"
    
    panel.ask_yes_no = mock_ask_yes_no
    
    # Mock controller
    panel.backup_controller = MagicMock()
    panel.backup_controller.restore_from_excel.return_value = True
    
    # Mock messagebox.showinfo
    messagebox_called = False
    def mock_show_message(message, title="Bilgi"):
        nonlocal messagebox_called
        messagebox_called = True
    
    panel.show_message = mock_show_message
    
    # Call the method
    panel.yedekten_yukle("excel")
    
    # Check that filedialog was called
    assert filedialog_called
    assert messagebox_called


def test_sifirla_veritabani_requires_confirmation(monkeypatch):
    """Test that sifirla_veritabani requires user confirmation"""
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)
    
    colors = {
        'background': '#fff',
        'surface': '#f7f7f7', 
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    panel = AyarlarPanel(parent=None, colors=colors)
    
    # Mock messagebox.askyesno to return False (user cancels)
    confirm_calls = 0
    def mock_ask_yes_no(message, title="Onay"):
        nonlocal confirm_calls
        confirm_calls += 1
        return False  # User cancels
    
    panel.ask_yes_no = mock_ask_yes_no
    
    # Mock controller
    panel.backup_controller = MagicMock()
    
    # Call the method
    panel.sifirla_veritabani()
    
    # Check that confirmation was asked
    assert confirm_calls == 1
    # Check that controller method was not called
    panel.backup_controller.reset_database.assert_not_called()