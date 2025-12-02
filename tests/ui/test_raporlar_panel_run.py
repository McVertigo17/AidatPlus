import pytest
from types import SimpleNamespace
from ui.raporlar_panel import RaporlarPanel
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

    def get_children(self):
        return list(range(len(self.rows)))

    def delete(self, item):
        # no-op
        pass

    def insert(self, parent, index, values):
        self.rows.append(values)
    
    # support kwargs such as tags
    def insert(self, parent, index, values, **kwargs):
        self.rows.append(values)

    def tag_configure(self, tag_name, **kwargs):
        # no-op for tags configuration
        pass


class DummyLabel:
    def __init__(self):
        self.text = None
    def configure(self, *args, **kwargs):
        # Accept both positional or keyword args (we expect keyword 'text')
        if 'text' in kwargs:
            self.text = kwargs['text']
        elif args:
            self.text = args[0]


def test_load_tum_islem_detaylari_populates_tree_and_labels(monkeypatch):
    # Patch BasePanel to avoid UI creation
    monkeypatch.setattr(BasePanel, '__init__', fake_base_init)

    colors = {
        'background': '#ffffff',
        'surface': '#f7f7f7',
        'primary': '#222',
        'text': '#333',
        'success': '#28a745',
        'error': '#dc3545'
    }

    panel = RaporlarPanel(parent=None, colors=colors)

    # Provide dummy UI attributes
    panel.islem_tree = DummyTree()
    panel.donem_toplam_gelir_label = DummyLabel()
    panel.donem_toplam_gider_label = DummyLabel()
    panel.donem_net_bakiye_label = DummyLabel()

    # Dummy financial entries
    class DummyKategori:
        def __init__(self, name, ana_kat_name):
            self.name = name
            self.ana_kategori = SimpleNamespace(name=ana_kat_name)

    class DummyHesap:
        def __init__(self, para_birimi='₺', ad='Hesap1'):
            self.para_birimi = para_birimi
            self.ad = ad

    from datetime import datetime as dt
    now = dt.now()
    gel1 = SimpleNamespace(id=1, tutar=100.0, tarih=now, kategori=DummyKategori('Aidat', 'Gelir'), hesap=DummyHesap(), aciklama='test')
    gid1 = SimpleNamespace(id=2, tutar=40.0, tarih=now, kategori=DummyKategori('Bakim','Gider'), hesap=DummyHesap(), aciklama='test')
    transfer = SimpleNamespace(id=3, tutar=10.0, tarih=now, kategori=None, hesap=DummyHesap(), hedef_hesap=None, aciklama='test')

    monkeypatch.setattr(panel, 'finans_controller', SimpleNamespace(
        get_gelirler=lambda: [gel1],
        get_giderler=lambda: [gid1],
        get_transferler=lambda: [transfer]
    ))

    # Ensure no filter combo boxes so default branch executes
    if hasattr(panel, 'islem_filtre_tur_combo'):
        panel.islem_filtre_tur_combo = None

    # Capture any error message instead of UI messagebox
    panel.last_error = None
    def capture_error(msg):
        panel.last_error = msg
    panel.show_error = capture_error

    # Run loader
    panel.load_tum_islem_detaylari()

    # Check there was no error
    assert panel.last_error is None
    # Check tree populated with 3 rows
    assert len(panel.islem_tree.rows) == 3

    # Check labels configured (strings contain numeric values)
    assert panel.donem_toplam_gelir_label.text is not None
    assert '100' in panel.donem_toplam_gelir_label.text or '100' in str(panel.donem_toplam_gelir_label.text)
    assert panel.donem_toplam_gider_label.text is not None

