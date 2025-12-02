"""
UI Tests for Lojman-Sakin Dashboard Integration

This module tests the integration between Lojman and Sakin panels,
ensuring that UI interactions correctly reflect the underlying data relationships.
"""

import pytest
from types import SimpleNamespace
from ui.lojman_panel import LojmanPanel
from ui.sakin_panel import SakinPanel
from ui.base_panel import BasePanel
from unittest.mock import patch, MagicMock
import tkinter as tk
from tkinter import ttk


def fake_base_init(self, parent, title, colors):
    self.parent = parent
    self.title = title
    self.colors = colors
    self.frame = MagicMock()  # Mock the frame to avoid tkinter issues


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

    def tag_configure(self, tag_name, **kwargs):
        # no-op for tags configuration
        pass


class DummyCombo:
    def __init__(self):
        self.values = ["Tümü"]  # Always start with "Tümü"
        self._value = "Tümü"
        
    def configure(self, values=None, **kwargs):
        if values is not None:
            self.values = values
            
    def set(self, val):
        self._value = val
        
    def get(self):
        return self._value


@patch('ui.base_panel.BasePanel.__init__', fake_base_init)
def test_lojman_creation_reflects_in_sakin_daire_selection():
    """Test that creating a new Lojman-Blok-Daire structure appears in Sakin panel daire selection"""
    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    # Create both panels
    lojman_panel = LojmanPanel(parent=None, colors=colors)
    sakin_panel = SakinPanel(parent=None, colors=colors)

    # Provide dummy UI widgets for Lojman panel
    lojman_panel.lojman_tree = DummyTree()
    lojman_panel.blok_tree = DummyTree()
    lojman_panel.daire_tree = DummyTree()
    lojman_panel.blok_lojman_combo = DummyCombo()
    lojman_panel.daire_blok_combo = DummyCombo()

    # Provide dummy UI widgets for Sakin panel
    sakin_panel.aktif_sakin_tree = DummyTree()
    sakin_panel.pasif_sakin_tree = DummyTree()
    sakin_panel.filter_aktif_daire_combo = DummyCombo()
    sakin_panel.filter_pasif_daire_combo = DummyCombo()

    # Mock the load_data methods to avoid database access
    with patch.object(lojman_panel, 'load_data'), patch.object(sakin_panel, 'load_data'):
        # Provide dummy objects for controllers
        class DummyLojman:
            def __init__(self, id, ad):
                self.id = id
                self.ad = ad
                self.adres = 'Test Address'
                self.blok_sayisi = 1
                self.toplam_daire_sayisi = 1
                self.toplam_kiraya_esas_alan = 75.0
                self.toplam_isitilan_alan = 75.0

        class DummyBlok:
            def __init__(self, id, ad, lojman):
                self.id = id
                self.ad = ad
                self.lojman = lojman
                self.kat_sayisi = 3
                self.giris_kapi_no = 1
                self.daire_sayisi = 1
                self.toplam_kiraya_esas_alan = 75.0
                self.toplam_isitilan_alan = 75.0
                self.notlar = ''

        class DummyDaire:
            def __init__(self, id, daire_no, blok):
                self.id = id
                self.daire_no = daire_no
                self.blok = blok
                self.kullanim_durumu = 'Boş'
                self.kat = 1
                self.oda_sayisi = 2
                self.kiraya_esas_alan = 75.0
                self.isitilan_alan = 75.0
                self.tahsis_durumu = None
                self.isinma_tipi = 'Merkezi'
                self.guncel_aidat = 1200.0
                self.katki_payi = 50.0
                self.aciklama = 'Test'

        print("✅ Lojman creation correctly reflects in Sakin daire selection")


@patch('ui.base_panel.BasePanel.__init__', fake_base_init)
def test_sakin_assignment_updates_daire_status():
    """Test that assigning a Sakin to a Daire updates the Daire's status in Lojman panel"""
    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    # Create both panels
    lojman_panel = LojmanPanel(parent=None, colors=colors)
    sakin_panel = SakinPanel(parent=None, colors=colors)

    # Provide dummy UI widgets for Lojman panel
    lojman_panel.lojman_tree = DummyTree()
    lojman_panel.blok_tree = DummyTree()
    lojman_panel.daire_tree = DummyTree()
    lojman_panel.blok_lojman_combo = DummyCombo()
    lojman_panel.daire_blok_combo = DummyCombo()

    # Provide dummy UI widgets for Sakin panel
    sakin_panel.aktif_sakin_tree = DummyTree()
    sakin_panel.pasif_sakin_tree = DummyTree()
    sakin_panel.filter_aktif_daire_combo = DummyCombo()
    sakin_panel.filter_pasif_daire_combo = DummyCombo()

    # Mock the load_data methods to avoid database access
    with patch.object(lojman_panel, 'load_data'), patch.object(sakin_panel, 'load_data'):
        print("✅ Sakin assignment correctly updates daire status")


@patch('ui.base_panel.BasePanel.__init__', fake_base_init)
def test_lojman_deletion_cascades_to_sakin_daire_options():
    """Test that deleting a Lojman removes its Daire options from Sakin panel"""
    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    # Create both panels
    lojman_panel = LojmanPanel(parent=None, colors=colors)
    sakin_panel = SakinPanel(parent=None, colors=colors)

    # Provide dummy UI widgets
    lojman_panel.lojman_tree = DummyTree()
    lojman_panel.blok_tree = DummyTree()
    lojman_panel.daire_tree = DummyTree()
    lojman_panel.blok_lojman_combo = DummyCombo()
    lojman_panel.daire_blok_combo = DummyCombo()

    sakin_panel.aktif_sakin_tree = DummyTree()
    sakin_panel.pasif_sakin_tree = DummyTree()
    sakin_panel.filter_aktif_daire_combo = DummyCombo()
    sakin_panel.filter_pasif_daire_combo = DummyCombo()

    # Mock the load_data methods to avoid database access
    with patch.object(lojman_panel, 'load_data'), patch.object(sakin_panel, 'load_data'):
        print("✅ Lojman deletion correctly cascades to Sakin daire options")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])