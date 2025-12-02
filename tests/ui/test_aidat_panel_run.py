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
    def get_children(self):
        return list(range(len(self.rows)))
    def delete(self, item):
        pass
    def insert(self, parent, index, values, **kwargs):
        self.rows.append(values)
    def tag_configure(self, tag_name, **kwargs):
        pass


class DummyLabel:
    def __init__(self):
        self.text = None
    def configure(self, *args, **kwargs):
        if 'text' in kwargs:
            self.text = kwargs['text']
        elif args:
            self.text = args[0]


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