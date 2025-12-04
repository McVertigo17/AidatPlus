import pytest
from ui.raporlar_panel import RaporlarPanel
from ui.base_panel import BasePanel


def fake_base_init(self, parent, title, colors):
    self.parent = parent
    self.title = title
    self.colors = colors
    self.frame = None


def test_raporlar_panel_controllers_instantiated(monkeypatch):
    # Replace BasePanel.__init__ so no UI widgets are created
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f0f0f0',
        'primary': '#333333',
        'text': '#000000',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = RaporlarPanel(parent=None, colors=colors)

    # Check controllers exist
    assert hasattr(panel, 'finans_controller')
    assert hasattr(panel, 'hesap_controller')
    assert hasattr(panel, 'sakin_controller')
    assert hasattr(panel, 'daire_controller')
    assert hasattr(panel, 'aidat_controller')
    assert hasattr(panel, 'kategori_controller')

def test_raporlar_panel_tabs_created(monkeypatch):
    # Replace BasePanel.__init__ so no UI widgets are created
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f0f0f0',
        'primary': '#333333',
        'text': '#000000',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = RaporlarPanel(parent=None, colors=colors)
    
    # Mock the tabview to avoid UI creation
    class MockTabView:
        def __init__(self):
            self.tabs = []
        
        def add(self, tab_name):
            self.tabs.append(tab_name)
            # Return a mock tab object
            class MockTab:
                def pack(self, **kwargs):
                    pass
                def pack_propagate(self, value):
                    pass
            return MockTab()
        
        def tab(self, tab_name):
            # Return a mock tab object
            class MockTab:
                def pack(self, **kwargs):
                    pass
                def pack_propagate(self, value):
                    pass
            return MockTab()
    
    panel.tabview = MockTabView()
    
    # Call setup_ui to create tabs
    panel.setup_ui()
    
    # Check all 5 tabs are created (removed unwanted tabs)
    expected_tabs = [
        "Tüm İşlem Detayları",
        "Bilanço",
        "İcmal",
        "Konut Mali Durumları",
        "Boş Konut Listesi"
    ]
    
    assert len(panel.tabview.tabs) == 5
    for tab in expected_tabs:
        assert tab in panel.tabview.tabs
def test_raporlar_panel_setup_methods_exist(monkeypatch):
    # Replace BasePanel.__init__ so no UI widgets are created
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f0f0f0',
        'primary': '#333333',
        'text': '#000000',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = RaporlarPanel(parent=None, colors=colors)
    
    # Check all setup methods exist
    setup_methods = [
        'setup_tum_islem_detaylari_tab',
        'setup_bilanco_tab',
        'setup_icmal_tab',
        'setup_konut_mali_durumlari_tab',
        'setup_bos_konut_listesi_tab'
    ]    
    for method_name in setup_methods:
        assert hasattr(panel, method_name), f"Method {method_name} should exist"
        
    # Check all load methods exist
    load_methods = [
        'load_tum_islem_detaylari',
        'load_bilanco',
        'load_icmal',
        'load_konut_mali_durumlari',
        'load_bos_konut_listesi',
]    
    for method_name in load_methods:
        assert hasattr(panel, method_name), f"Method {method_name} should exist"
