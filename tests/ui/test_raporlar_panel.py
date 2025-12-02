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
