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
        self.values = []
        self._value = None
    def configure(self, values=None, **kwargs):
        if values is not None:
            self.values = values
    def set(self, val):
        self._value = val
    def get(self):
        return self._value


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
    assert panel.daire_blok_combo.values and 'Lojman 1' in panel.daire_blok_combo.values[0]
