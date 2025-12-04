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


def test_load_bilanco_populates_tree_and_labels(monkeypatch):
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
    panel.bilanco_tree = DummyTree()
    panel.bilanco_onceki_bakiye_label = DummyLabel()
    panel.bilanco_donem_gelir_label = DummyLabel()
    panel.bilanco_donem_gider_label = DummyLabel()
    panel.bilanco_son_bakiye_label = DummyLabel()

    # Dummy financial entries
    class DummyKategori:
        def __init__(self, name, ana_kat_name):
            self.name = name
            self.ana_kategori = SimpleNamespace(name=ana_kat_name)

    from datetime import datetime as dt
    now = dt.now()
    gel1 = SimpleNamespace(id=1, tutar=100.0, tarih=now, kategori=DummyKategori('Aidat', 'Gelir'))
    gid1 = SimpleNamespace(id=2, tutar=40.0, tarih=now, kategori=DummyKategori('Bakim','Gider'))

    monkeypatch.setattr(panel, 'finans_controller', SimpleNamespace(
        get_gelirler=lambda: [gel1],
        get_giderler=lambda: [gid1]
    ))

    # Ensure no filter combo boxes so default branch executes
    if hasattr(panel, 'bilanco_filtre_tur_combo'):
        panel.bilanco_filtre_tur_combo = None

    # Capture any error message instead of UI messagebox
    panel.last_error = None
    def capture_error(msg):
        panel.last_error = msg
    panel.show_error = capture_error

    # Run loader
    panel.load_bilanco()

    # Check there was no error
    assert panel.last_error is None
    # Check tree populated with 2 rows (1 gelir, 1 gider)
    assert len(panel.bilanco_tree.rows) == 2

    # Check labels configured
    assert panel.bilanco_onceki_bakiye_label.text is not None
    assert panel.bilanco_donem_gelir_label.text is not None
    assert panel.bilanco_donem_gider_label.text is not None
    assert panel.bilanco_son_bakiye_label.text is not None

def test_load_icmal_populates_tree_and_labels(monkeypatch):
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
    panel.icmal_tree = DummyTree()
    panel.icmal_gider_toplam_label = DummyLabel()

    # Dummy financial entries
    class DummyKategori:
        def __init__(self, name, ana_kat_name):
            self.name = name
            self.ana_kategori = SimpleNamespace(name=ana_kat_name)

    from datetime import datetime as dt
    now = dt.now()
    gid1 = SimpleNamespace(id=1, tutar=100.0, tarih=now, kategori=DummyKategori('Bakim','Gider'), aciklama='test')

    monkeypatch.setattr(panel, 'finans_controller', SimpleNamespace(
        get_giderler=lambda: [gid1]
    ))

    # Ensure no filter combo boxes so default branch executes
    if hasattr(panel, 'icmal_filtre_tur_combo'):
        panel.icmal_filtre_tur_combo = None

    # Capture any error message instead of UI messagebox
    panel.last_error = None
    def capture_error(msg):
        panel.last_error = msg
    panel.show_error = capture_error

    # Run loader
    panel.load_icmal()

    # Check there was no error
    assert panel.last_error is None
    # Check tree populated
    assert len(panel.icmal_tree.rows) >= 1

    # Check labels configured
    assert panel.icmal_gider_toplam_label.text is not None

def test_load_konut_mali_durumlari_populates_trees(monkeypatch):
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
    panel.konut_durum_tree = DummyTree()
    panel.maliyet_tree = DummyTree()

    # Dummy entries
    class DummySakin:
        def __init__(self, daire_id=None, tahsis_tarihi=None, giris_tarihi=None, cikis_tarihi=None):
            self.daire_id = daire_id
            self.tahsis_tarihi = tahsis_tarihi
            self.giris_tarihi = giris_tarihi
            self.cikis_tarihi = cikis_tarihi

    class DummyDaire:
        def __init__(self, id, daire_no, kiraya_esas_alan=None, aktif=True):
            self.id = id
            self.daire_no = daire_no
            self.kiraya_esas_alan = kiraya_esas_alan
            self.aktif = aktif
            self.sakini = None

    # Mock database session
    def mock_get_db():
        class MockSession:
            def query(self, model):
                return self
            
            def options(self, *args):
                return self
            
            def filter(self, condition):
                return self
            
            def all(self):
                if 'Daire' in str(type(self)):
                    return [DummyDaire(1, '1A', 100, True)]
                return []
            
            def close(self):
                pass
        
        return MockSession()

    monkeypatch.setattr('ui.raporlar_panel.get_db', mock_get_db)
    
    monkeypatch.setattr(panel, 'daire_controller', SimpleNamespace())
    monkeypatch.setattr(panel, 'finans_controller', SimpleNamespace(
        get_giderler=lambda: []
    ))

    # Ensure no filter combo boxes so default branch executes
    if hasattr(panel, 'konut_mali_filtre_tur_combo'):
        panel.konut_mali_filtre_tur_combo = None

    # Capture any error message instead of UI messagebox
    panel.last_error = None
    def capture_error(msg):
        panel.last_error = msg
    panel.show_error = capture_error

    # Run loader
    panel.load_konut_mali_durumlari()

    # Check there was no error
    assert panel.last_error is None
    # Check trees populated
    assert len(panel.konut_durum_tree.rows) >= 1
    assert len(panel.maliyet_tree.rows) >= 1

def test_load_bos_konut_listesi_populates_tree(monkeypatch):
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
    panel.bos_konut_tree = DummyTree()

    # Mock database session
    def mock_get_db():
        class MockSession:
            def query(self, model):
                return self
            
            def options(self, *args):
                return self
            
            def filter(self, condition):
                return self
            
            def all(self):
                # Return minimal data for testing
                return []
            
            def close(self):
                pass
        
        return MockSession()

    monkeypatch.setattr('ui.raporlar_panel.get_db', mock_get_db)
    
    # Ensure no filter combo boxes so default branch executes
    if hasattr(panel, 'bos_konut_yil_combo'):
        panel.bos_konut_yil_combo = None

    # Capture any error message instead of UI messagebox
    panel.last_error = None
    def capture_error(msg):
        panel.last_error = msg
    panel.show_error = capture_error

    # Run loader
    panel.load_bos_konut_listesi()

    # Check there was no error
    assert panel.last_error is None
    # Check tree populated
    assert len(panel.bos_konut_tree.rows) >= 1  # At least the "no empty units" message

def test_load_kategori_dagilimi_executes_without_error(monkeypatch):
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

    # Dummy financial entries
    class DummyKategori:
        def __init__(self, name, ana_kat_name):
            self.name = name
            self.ana_kategori = SimpleNamespace(name=ana_kat_name)

    from datetime import datetime as dt
    now = dt.now()
    gel1 = SimpleNamespace(id=1, tutar=100.0, tarih=now, kategori=DummyKategori('Aidat', 'Gelir'))
    gid1 = SimpleNamespace(id=2, tutar=40.0, tarih=now, kategori=DummyKategori('Bakim','Gider'))

    monkeypatch.setattr(panel, 'finans_controller', SimpleNamespace(
        get_gelirler=lambda: [gel1],
        get_giderler=lambda: [gid1]
    ))

    # Capture any error message instead of UI messagebox
    panel.last_error = None
    def capture_error(msg):
        panel.last_error = msg
    panel.show_error = capture_error

    # Run loader
    panel.load_kategori_dagilimi()

    # Check there was no error
    assert panel.last_error is None

def test_load_aylik_ozet_executes_without_error(monkeypatch):
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

    # Dummy financial entries
    class DummyKategori:
        def __init__(self, name, ana_kat_name):
            self.name = name
            self.ana_kategori = SimpleNamespace(name=ana_kat_name)

    from datetime import datetime as dt
    now = dt.now()
    gel1 = SimpleNamespace(id=1, tutar=100.0, tarih=now, kategori=DummyKategori('Aidat', 'Gelir'))
    gid1 = SimpleNamespace(id=2, tutar=40.0, tarih=now, kategori=DummyKategori('Bakim','Gider'))

    monkeypatch.setattr(panel, 'finans_controller', SimpleNamespace(
        get_gelirler=lambda: [gel1],
        get_giderler=lambda: [gid1]
    ))

    # Ensure no filter combo boxes so default branch executes
    if hasattr(panel, 'aylik_ozet_yil_combo'):
        panel.aylik_ozet_yil_combo = None

    # Capture any error message instead of UI messagebox
    panel.last_error = None
    def capture_error(msg):
        panel.last_error = msg
    panel.show_error = capture_error

    # Run loader
    panel.load_aylik_ozet()

    # Check there was no error
    assert panel.last_error is None

def test_load_trend_analizi_executes_without_error(monkeypatch):
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

    # Dummy financial entries
    class DummyKategori:
        def __init__(self, name, ana_kat_name):
            self.name = name
            self.ana_kategori = SimpleNamespace(name=ana_kat_name)

    from datetime import datetime as dt
    now = dt.now()
    gel1 = SimpleNamespace(id=1, tutar=100.0, tarih=now, kategori=DummyKategori('Aidat', 'Gelir'))
    gid1 = SimpleNamespace(id=2, tutar=40.0, tarih=now, kategori=DummyKategori('Bakim','Gider'))

    monkeypatch.setattr(panel, 'finans_controller', SimpleNamespace(
        get_gelirler=lambda: [gel1],
        get_giderler=lambda: [gid1]
    ))

    # Ensure no filter combo boxes so default branch executes
    if hasattr(panel, 'trend_analizi_yil_combo'):
        panel.trend_analizi_yil_combo = None

    # Capture any error message instead of UI messagebox
    panel.last_error = None
    def capture_error(msg):
        panel.last_error = msg
    panel.show_error = capture_error

    # Run loader
    panel.load_trend_analizi()

    # Check there was no error
    assert panel.last_error is None

