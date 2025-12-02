"""
Finans paneli
"""

import customtkinter as ctk
from tkinter import ttk, Menu, Toplevel, filedialog
import tkinter as tk
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from ui.base_panel import BasePanel
from ui.error_handler import (
    ErrorHandler, handle_exception, show_error, show_success, show_warning,
    UIValidator
)
from controllers.hesap_controller import HesapController
from controllers.finans_islem_controller import FinansIslemController
from controllers.kategori_yonetim_controller import KategoriYonetimController
from controllers.belge_controller import BelgeController
from models.base import Hesap, FinansIslem, AnaKategori
from models.validation import Validator
from models.exceptions import (
    ValidationError, DatabaseError, NotFoundError, DuplicateError, BusinessLogicError
)


class FinansPanel(BasePanel):
    """Finans yönetimi paneli
    
    Gelir, gider ve transfer işlemlerinin yönetimini sağlar.
    İki sekmeden oluşur: Hesap Yönetimi ve İşlemler
    
    Attributes:
        hesap_controller (HesapController): Hesap yönetim denetleyicisi
        finans_controller (FinansIslemController): Finansal işlem denetleyicisi
        kategori_controller (KategoriYonetimController): Kategori yönetim denetleyicisi
        belge_controller (BelgeController): Belge yönetim denetleyicisi
        aktif_hesaplar (List[Hesap]): Aktif hesaplar listesi
        pasif_hesaplar (List[Hesap]): Pasif hesaplar listesi
        gelirler (List[FinansIslem]): Gelir işlemleri listesi
        giderler (List[FinansIslem]): Gider işlemleri listesi
    """

    def __init__(self, parent: ctk.CTk, colors: Dict[str, str]) -> None:
        self.hesap_controller = HesapController()
        self.finans_controller = FinansIslemController()
        self.kategori_controller = KategoriYonetimController()
        self.belge_controller = BelgeController()

        # Veri saklama
        self.aktif_hesaplar: List[Hesap] = []
        self.pasif_hesaplar: List[Hesap] = []
        self.ana_kategoriler: List[AnaKategori] = []
        self.gelirler: List[FinansIslem] = []
        self.giderler: List[FinansIslem] = []
        self.duzenlenen_islem_id = None
        self.tum_islemler_verisi: List[Tuple[str, FinansIslem]] = []  # Tüm işlemlerin orijinal listesi
        self.secili_belge_yolu: Optional[str] = None  # Seçili belgenin yolu
        
        # Filtre değişkenleri
        self.filter_tur = "Tümü"
        self.filter_hesap = "Tümü"
        self.filter_aciklama = ""

        super().__init__(parent, "💰 Finans Yönetimi", colors)

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_hesaplar()
        self.load_ana_kategoriler()
        self.load_islemler()

    def load_ana_kategoriler(self) -> None:
        """Ana kategorileri yükle"""
        self.ana_kategoriler = self.kategori_controller.get_ana_kategoriler()

    def setup_ui(self) -> None:
        """UI'yi oluştur"""
        # Ana container
        main_frame = ctk.CTkFrame(self.frame, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab kontrolü
        self.tabview = ctk.CTkTabview(main_frame, width=1000, height=600)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab'ları oluştur
        self.tabview.add("Hesap Yönetimi")
        self.tabview.add("İşlemler")

        # Tab içeriklerini oluştur
        self.setup_hesap_yonetimi_tab()
        self.setup_islemler_tab()

        # Başlangıç verilerini yükle
        self.load_data()

    def setup_hesap_yonetimi_tab(self) -> None:
        """Hesap yönetimi tab'ı"""
        tab = self.tabview.tab("Hesap Yönetimi")

        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Yeni hesap ekleme butonu
        add_button = ctk.CTkButton(
            main_frame,
            text="➕ Yeni Hesap Ekle",
            command=self.open_yeni_hesap_modal,
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"],
            height=40
        )
        add_button.pack(pady=(10, 5))

        # Hesap listesi
        self.hesap_tree = ttk.Treeview(
            main_frame,
            columns=("id", "ad", "tur", "bakiye", "para_birimi", "durum", "varsayilan"),
            show="headings",
            height=15
        )

        # Kolon başlıkları
        self.hesap_tree.heading("id", text="ID")
        self.hesap_tree.heading("ad", text="Hesap Adı")
        self.hesap_tree.heading("tur", text="Hesap Türü")
        self.hesap_tree.heading("bakiye", text="Bakiye")
        self.hesap_tree.heading("para_birimi", text="Para Birimi")
        self.hesap_tree.heading("durum", text="Durum")
        self.hesap_tree.heading("varsayilan", text="Varsayılan")

        # Kolon genişlikleri ve hizalanması
        self.hesap_tree.column("id", width=50, anchor="center")
        self.hesap_tree.column("ad", width=200, anchor="center")
        self.hesap_tree.column("tur", width=150, anchor="center")
        self.hesap_tree.column("bakiye", width=120, anchor="center")
        self.hesap_tree.column("para_birimi", width=100, anchor="center")
        self.hesap_tree.column("durum", width=100, anchor="center")
        self.hesap_tree.column("varsayilan", width=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.hesap_tree.yview)
        self.hesap_tree.configure(yscrollcommand=scrollbar.set)

        self.hesap_tree.pack(side="left", fill="both", expand=True, padx=10, pady=(10, 10))
        scrollbar.pack(side="right", fill="y", pady=(10, 10))

        # Sağ tık menüsü
        self.hesap_context_menu = Menu(main_frame, tearoff=0)
        # Menü seçenekleri dinamik olarak eklenecek

        self.hesap_tree.bind("<Button-3>", self.show_hesap_context_menu)

    def setup_islemler_tab(self) -> None:
        """İşlemler tab'ı - Birleşik gelir/gider/transfer işlemleri"""
        tab = self.tabview.tab("İşlemler")

        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Üst butonlar alanı
        buttons_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        buttons_frame.pack(fill="x", padx=10, pady=(10, 5))

        # İşlem ekleme butonları
        gelir_btn = ctk.CTkButton(
            buttons_frame,
            text="💰 Gelir Ekle",
            command=self.open_gelir_modal,
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        gelir_btn.pack(side="left", padx=(0, 5))

        gider_btn = ctk.CTkButton(
            buttons_frame,
            text="💸 Gider Ekle",
            command=self.open_gider_modal,
            fg_color=self.colors["error"],
            hover_color=self.colors["primary"],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        gider_btn.pack(side="left", padx=(0, 5))

        self.transfer_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Transfer Ekle",
            command=self.open_transfer_modal,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.transfer_btn.pack(side="left", padx=(0, 5))

        # İşlemler tablosu - Scrollable frame ile
        table_frame = ctk.CTkScrollableFrame(main_frame, fg_color=self.colors["background"])
        table_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # İşlemler tablosu
        self.islemler_tree = ttk.Treeview(
            table_frame,
            columns=("id", "tur", "tarih", "ana_kategori", "alt_kategori", "hesap", "tutar", "belge", "aciklama"),
            show="headings",
            height=20
        )

        # Kolon başlıkları
        self.islemler_tree.heading("id", text="ID")
        self.islemler_tree.heading("tur", text="Tür")
        self.islemler_tree.heading("tarih", text="Tarih")
        self.islemler_tree.heading("ana_kategori", text="Ana Kategori")
        self.islemler_tree.heading("alt_kategori", text="Alt Kategori")
        self.islemler_tree.heading("hesap", text="Hesap")
        self.islemler_tree.heading("tutar", text="Tutar")
        self.islemler_tree.heading("belge", text="📎")
        self.islemler_tree.heading("aciklama", text="Açıklama")

        # Kolon genişlikleri ve hizalanması
        self.islemler_tree.column("id", width=50, anchor="center")
        self.islemler_tree.column("tur", width=30, anchor="center")
        self.islemler_tree.column("tarih", width=50, anchor="center")
        self.islemler_tree.column("ana_kategori", width=120, anchor="center")
        self.islemler_tree.column("alt_kategori", width=120, anchor="center")
        self.islemler_tree.column("hesap", width=150, anchor="center")
        self.islemler_tree.column("tutar", width=50, anchor="center")
        self.islemler_tree.column("belge", width=15, anchor="center")
        self.islemler_tree.column("aciklama", width=350, anchor="center")

        # Treeview'i scrollable frame'e yerleştir
        self.islemler_tree.pack(fill="both", expand=True)

        # Sağ tık menüsü
        self.islemler_context_menu = Menu(tab, tearoff=0)
        self.islemler_context_menu.add_command(label="Düzenle", command=self.duzenle_islem)
        self.islemler_context_menu.add_command(label="Sil", command=self.sil_islem)

        self.islemler_tree.bind("<Button-3>", self.show_islemler_context_menu)
        
        # Çift tıkla - belge aç
        self.islemler_tree.bind("<Double-1>", self.double_click_islem)

        # Filtreleme paneli (alt taraf)
        self.setup_filtreleme_paneli(main_frame)

    def load_hesaplar(self) -> None:
        """Hesapları yükle - aktif ve pasif hesapları tek tabloda göster"""
        # Widget'ın geçerli olup olmadığını kontrol et
        if not hasattr(self, 'hesap_tree') or self.hesap_tree is None:
            return
        
        try:
            for item in self.hesap_tree.get_children():
                self.hesap_tree.delete(item)
        except tk.TclError:
            # Widget geçersizse, işlemi atla
            return

        # Aktif hesaplar
        self.aktif_hesaplar = self.hesap_controller.get_aktif_hesaplar()
        # En son eklenen en üstte olacak şekilde sırala (ID'ye göre azalan)
        self.aktif_hesaplar.sort(key=lambda x: x.id, reverse=True)
        
        for hesap in self.aktif_hesaplar:
            self.hesap_tree.insert("", "end", values=(
                hesap.id,
                hesap.ad,
                hesap.tur,
                f"{hesap.bakiye:.2f}",
                hesap.para_birimi if hasattr(hesap, 'para_birimi') else "₺",
                "Aktif",
                "✓" if hesap.varsayilan else ""
            ), tags=("aktif",))

        # Pasif hesaplar
        self.pasif_hesaplar = self.hesap_controller.get_pasif_hesaplar()
        # En son eklenen en üstte olacak şekilde sırala (ID'ye göre azalan)
        self.pasif_hesaplar.sort(key=lambda x: x.id, reverse=True)
        
        for hesap in self.pasif_hesaplar:
            self.hesap_tree.insert("", "end", values=(
                hesap.id,
                hesap.ad,
                hesap.tur,
                f"{hesap.bakiye:.2f}",
                hesap.para_birimi if hasattr(hesap, 'para_birimi') else "₺",
                "Pasif",
                "✓" if hesap.varsayilan else ""
            ), tags=("pasif",))

        # Renk kodlaması - pasif hesaplar açık gri
        self.hesap_tree.tag_configure("aktif", background="#ffffff")  # Beyaz
        self.hesap_tree.tag_configure("pasif", background="#f0f0f0")  # Açık gri

    def load_islemler(self) -> None:
        """Tüm işlemleri yükle - gelir, gider ve transferler"""
        # Widget'ın geçerli olup olmadığını kontrol et
        if not hasattr(self, 'islemler_tree') or self.islemler_tree is None:
            return
        
        try:
            for item in self.islemler_tree.get_children():
                self.islemler_tree.delete(item)
        except tk.TclError:
            # Widget geçersizse, işlemi atla
            return

        # Gelirleri, giderleri ve transferleri yükle
        self.gelirler = self.finans_controller.get_gelirler()
        self.giderler = self.finans_controller.get_giderler()
        self.transferler = self.finans_controller.get_transferler()

        # Tüm işlemleri birleştir ve tarihe göre sırala (en yeni en üstte)
        tum_islemler = []
        for gelir in self.gelirler:
            tum_islemler.append(('gelir', gelir))
        for gider in self.giderler:
            tum_islemler.append(('gider', gider))
        for transfer in self.transferler:
            tum_islemler.append(('transfer', transfer))

        # ID göre sırala (en büyük en üstte)
        tum_islemler.sort(key=lambda x: x[1].id, reverse=True)
        
        # Tüm işlemleri saklası (filtreleme için)
        self.tum_islemler_verisi = tum_islemler
        
        # İşlem ID ve türü eşleme (gerçek ID bulma için)
        self.islem_id_map = {}  # TreeView row ID'den gerçek işlem bilgisine

        # Sıralanmış işlemleri tabloya ekle
        for islem_tur, islem in tum_islemler:
            # İşlem tutarını para birimiyle birlikte göster
            tutar_gosterimi = f"{islem.tutar:.2f}"
            if islem.hesap and hasattr(islem.hesap, 'para_birimi'):
                tutar_gosterimi = f"{islem.tutar:.2f} {islem.hesap.para_birimi}"
            
            # Belge göstergesi
            belge_gostergesi = "📎" if (hasattr(islem, 'belge_yolu') and islem.belge_yolu) else ""
            
            if islem_tur == 'gelir':
                row_id = self.islemler_tree.insert("", "end", values=(
                    f"İşlem#{islem.id}",
                    "Gelir",
                    islem.tarih.strftime("%d.%m.%Y") if islem.tarih else "",
                    (islem.kategori.ana_kategori.name if islem.kategori and islem.kategori.ana_kategori else islem.ana_kategori_text or ""),
                    islem.kategori.name if islem.kategori else "",
                    islem.hesap.ad if islem.hesap else "",
                    tutar_gosterimi,
                    belge_gostergesi,
                    islem.aciklama or ""
                ), tags=("gelir",))
                self.islem_id_map[row_id] = {'tur': 'gelir', 'id': islem.id}
            elif islem_tur == 'gider':
                row_id = self.islemler_tree.insert("", "end", values=(
                    f"İşlem#{islem.id}",
                    "Gider",
                    islem.tarih.strftime("%d.%m.%Y") if islem.tarih else "",
                    (islem.kategori.ana_kategori.name if islem.kategori and islem.kategori.ana_kategori else islem.ana_kategori_text or ""),
                    islem.kategori.name if islem.kategori else "",
                    islem.hesap.ad if islem.hesap else "",
                    tutar_gosterimi,
                    belge_gostergesi,
                    islem.aciklama or ""
                ), tags=("gider",))
                self.islem_id_map[row_id] = {'tur': 'gider', 'id': islem.id}
            else:  # transfer
                # Transfer işlemleri için kaynak ve hedef hesapların para birimlerini göster
                transfer_tutar = f"{islem.tutar:.2f}"
                if islem.hesap and hasattr(islem.hesap, 'para_birimi'):
                    transfer_tutar = f"{islem.tutar:.2f} {islem.hesap.para_birimi}"
                
                row_id = self.islemler_tree.insert("", "end", values=(
                    f"İşlem#{islem.id}",
                    "Transfer",
                    islem.tarih.strftime("%d.%m.%Y") if islem.tarih else "",
                    "",  # Ana kategori yok
                    "",  # Alt kategori yok
                    f"{islem.hesap.ad if islem.hesap else ''} → {islem.hedef_hesap.ad if islem.hedef_hesap else ''}",
                    transfer_tutar,
                    belge_gostergesi,
                    islem.aciklama or ""
                ), tags=("transfer",))
                self.islem_id_map[row_id] = {'tur': 'transfer', 'id': islem.id}

        # Renk kodlaması
        self.islemler_tree.tag_configure("gelir", background="#e8f5e8")  # Açık yeşil
        self.islemler_tree.tag_configure("gider", background="#ffeaea")  # Açık kırmızı
        self.islemler_tree.tag_configure("transfer", background="#e8f0ff")  # Açık mavi

        # Hesap filtre combo'sunu güncelle
        if hasattr(self, 'filter_hesap_combo'):
            hesap_listesi = set()
            for _, islem in tum_islemler:
                if islem.hesap:
                    hesap_listesi.add(islem.hesap.ad)
            hesap_options = ["Tümü"] + sorted(list(hesap_listesi))
            self.filter_hesap_combo.configure(values=hesap_options)

        # Transfer butonunu aktif/pasif yap (en az 2 hesap varsa aktif)
        if hasattr(self, 'transfer_btn') and len(self.aktif_hesaplar) >= 2:
            self.transfer_btn.configure(state="normal", fg_color=self.colors["primary"])
        elif hasattr(self, 'transfer_btn'):
            self.transfer_btn.configure(state="disabled", fg_color=self.colors["text_secondary"])

    # Scroll fonksiyonu
    def scroll_to_bottom(self) -> None:
        """Tabloyu en alta kaydır"""
        try:
            # Scrollable frame'in alt kısmına git
            self.islemler_tree.yview_moveto(1.0)
        except:
            pass

    # Context menu handlers
    def show_hesap_context_menu(self, event: tk.Event) -> None:
        """Hesap tablosu için dinamik sağ tık menüsü"""
        try:
            # Mevcut menü öğelerini temizle
            self.hesap_context_menu.delete(0, 'end')

            # Seçili öğeyi al
            selection = self.hesap_tree.selection()
            if not selection:
                return

            item = self.hesap_tree.item(selection[0])
            values = item['values']
            hesap_durum = values[5]  # Durum sütunu (Aktif/Pasif)
            hesap_varsayilan = values[6] == "✓"  # Varsayılan sütunu

            # Menü öğelerini hesap durumuna göre ekle
            self.hesap_context_menu.add_command(label="Düzenle", command=self.duzenle_hesap)

            if hesap_durum == "Aktif":
                if hesap_varsayilan:
                    self.hesap_context_menu.add_command(label="Varsayılan Hesabı Kaldır", command=self.varsayilan_hesap_kaldir)
                else:
                    self.hesap_context_menu.add_command(label="Varsayılan Hesap Yap", command=self.varsayilan_hesap_yap)
                    self.hesap_context_menu.add_command(label="Pasif Yap", command=self.pasif_hesap_yap)
            else:  # Pasif
                self.hesap_context_menu.add_command(label="Aktif Yap", command=self.aktif_hesap_yap)
                self.hesap_context_menu.add_command(label="Sil", command=self.sil_hesap)

            # Menüyü göster
            self.hesap_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.hesap_context_menu.grab_release()

    def show_islemler_context_menu(self, event: tk.Event) -> None:
        """İşlemler tablosu için sağ tık menüsü"""
        try:
            self.islemler_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.islemler_context_menu.grab_release()

    # Hesap işlemler
    def varsayilan_hesap_yap(self) -> None:
        """Seçili hesabı varsayılan yap"""
        selection = self.hesap_tree.selection()
        if not selection:
            self.show_error("Lütfen varsayılan yapılacak hesabı seçin!")
            return

        hesap_id = int(self.hesap_tree.item(selection[0])['values'][0])

        # Hesabı varsayılan yap
        success = self.hesap_controller.set_varsayilan_hesap(hesap_id)
        if success:
            self.show_message(f"Hesap #{hesap_id} varsayılan yapıldı!")
        else:
            self.show_error(f"Hesap #{hesap_id} varsayılan yapılamadı!")
        self.load_data()

    def varsayilan_hesap_kaldir(self) -> None:
        """Seçili hesabın varsayılan olma durumunu kaldır"""
        selection = self.hesap_tree.selection()
        if not selection:
            self.show_error("Lütfen varsayılan hesabı kaldırılacak hesabı seçin!")
            return

        hesap_id = int(self.hesap_tree.item(selection[0])['values'][0])

        # Hesabı varsayılan olmaktan çıkar
        data = {'varsayilan': False}
        self.hesap_controller.update(hesap_id, data)
        self.show_message(f"Hesap #{hesap_id} varsayılan olmaktan çıkarıldı!")
        self.load_data()

    def duzenle_hesap(self) -> None:
        """Seçili hesabı düzenle"""
        selection = self.hesap_tree.selection()
        if not selection:
            self.show_error("Lütfen düzenlenecek hesabı seçin!")
            return

        hesap_id = self.hesap_tree.item(selection[0])['values'][0]
        hesap = next((h for h in (self.aktif_hesaplar + self.pasif_hesaplar) if h.id == hesap_id), None)

        if hesap:
            self.open_hesap_modal(hesap)
        else:
            self.show_error("Hesap bulunamadı!")

    def pasif_hesap_yap(self) -> None:
        """Seçili hesabı pasif yap"""
        selection = self.hesap_tree.selection()
        if not selection:
            self.show_error("Lütfen pasif yapılacak hesabı seçin!")
            return

        values = self.hesap_tree.item(selection[0])['values']
        hesap_id = int(values[0])
        hesap_durum = values[5]

        if hesap_durum == "Pasif":
            self.show_error("Bu hesap zaten pasif durumda!")
            return

        # Hesabı pasif yap
        data = {'aktif': False}
        self.hesap_controller.update(hesap_id, data)
        self.show_message(f"Hesap #{hesap_id} pasif yapıldı!")
        self.load_data()

    def aktif_hesap_yap(self) -> None:
        """Seçili hesabı aktif yap"""
        selection = self.hesap_tree.selection()
        if not selection:
            self.show_error("Lütfen aktif yapılacak hesabı seçin!")
            return

        values = self.hesap_tree.item(selection[0])['values']
        hesap_id = int(values[0])
        hesap_durum = values[5]

        if hesap_durum == "Aktif":
            self.show_error("Bu hesap zaten aktif durumda!")
            return

        # Hesabı aktif yap
        data = {'aktif': True}
        self.hesap_controller.update(hesap_id, data)
        self.show_message(f"Hesap #{hesap_id} aktif yapıldı!")
        self.load_data()

    def sil_hesap(self) -> None:
        """Seçili hesabı sil"""
        selection = self.hesap_tree.selection()
        if not selection:
            self.show_error("Lütfen silinecek hesabı seçin!")
            return

        values = self.hesap_tree.item(selection[0])['values']
        hesap_id = int(values[0])
        hesap_durum = values[5]

        if hesap_durum == "Aktif":
            self.show_error("Aktif hesapları silemezsiniz. Önce pasif yapınız!")
            return

        if self.ask_yes_no(f"Hesap #{hesap_id} gerçekten silinsin mi?"):
                # Hesabı sil
                success = self.hesap_controller.delete(hesap_id)
                if success:
                    self.show_message(f"Hesap #{hesap_id} silindi!")
                else:
                    self.show_error(f"Hesap #{hesap_id} silinemedi!")
                self.load_data()

    # Finans işlemleri
    def duzenle_islem(self) -> None:
         """Seçili işlemi düzenle"""
         selection = self.islemler_tree.selection()
         if not selection:
             self.show_error("Lütfen düzenlenecek işlemi seçin!")
             return

         # TreeView row ID'den işlem bilgisini al
         row_id = selection[0]
         if row_id not in self.islem_id_map:
             self.show_error("İşlem bulunamadı!")
             return
         
         islem_info = self.islem_id_map[row_id]
         islem_tur = islem_info['tur']
         islem_id = islem_info['id']

         # Doğru liste'den işlemi bul
         islem = None
         if islem_tur == 'gelir':
             islem = next((g for g in self.gelirler if g.id == islem_id), None)
         elif islem_tur == 'gider':
             islem = next((g for g in self.giderler if g.id == islem_id), None)
         elif islem_tur == 'transfer':
             islem = next((t for t in self.transferler if t.id == islem_id), None)

         if islem:
             # Düzenleme modunu belirt ve işlem ID'sini sakla
             self.duzenleme_modu = True
             self.duzenlenen_islem_id = islem_id
             
             if islem_tur == 'gelir':
                 self.open_gelir_modal(islem)
             elif islem_tur == 'gider':
                 self.open_gider_modal(islem)
             elif islem_tur == 'transfer':
                 self.open_transfer_modal(islem)
         else:
             self.show_error("İşlem bulunamadı!")

    def sil_islem(self) -> None:
        """Seçili işlemi sil"""
        selection = self.islemler_tree.selection()
        if not selection:
            self.show_error("Lütfen silinecek işlemi seçin!")
            return

        # TreeView row ID'den işlem bilgisini al
        row_id = selection[0]
        if row_id not in self.islem_id_map:
            self.show_error("İşlem bulunamadı!")
            return
        
        islem_info = self.islem_id_map[row_id]
        islem_tur = islem_info['tur']
        islem_id = islem_info['id']
        
        # Türü Türkçeleştir
        tur_text = {'gelir': 'Gelir', 'gider': 'Gider', 'transfer': 'Transfer'}.get(islem_tur, 'İşlem')
        mesaj = f"{tur_text} işlemi #{islem_id}"

        if self.ask_yes_no(f"{mesaj} gerçekten silinsin mi?"):
            # İşlemi sil
            success = self.finans_controller.delete(islem_id)
            if success:
                self.show_message(f"{mesaj} silindi!")
            else:
                self.show_error(f"{mesaj} silinemedi!")
            self.load_data()

    def double_click_islem(self, event: tk.Event) -> None:
        """Satıra çift tıklama - belge ikonuna tıklandıysa belgeyi aç"""
        selection = self.islemler_tree.selection()
        if not selection:
            return

        values = self.islemler_tree.item(selection[0])['values']
        
        # Tıklandığı kolon kontrol et - identify_column '#6' gibi string döndürür
        kolon_str = self.islemler_tree.identify_column(event.x)
        try:
            kolon_index = int(kolon_str.replace('#', ''))
        except (ValueError, AttributeError):
            # Hata varsa hiçbir şey yapma
            return
        
        # Sadece belge kolonu (#8) ve belge göstergesi varsa belgeyi aç
        if kolon_index == 8:  # Belge kolonu (8. kolon, index 7)
            belge_gostergesi = values[7]
            if belge_gostergesi == "📎":
                # Belgeyi aç
                self._ac_islem_belgesi(selection[0])

    def _ac_islem_belgesi(self, item_id: str) -> None:
        """İşlemin belgesini aç"""
        # islem_id_map'den işlem bilgisini al
        if item_id not in self.islem_id_map:
            self.show_error("İşlem bulunamadı!")
            return
        
        islem_info = self.islem_id_map[item_id]
        islem_id = islem_info['id']
        islem_tur = islem_info['tur']
        
        # tum_islemler_verisi'nde işlemi bul
        for tur, islem in self.tum_islemler_verisi:
            if tur == islem_tur and islem.id == islem_id:
                if hasattr(islem, 'belge_yolu') and islem.belge_yolu:
                    basarili, mesaj = self.belge_controller.dosya_ac(islem.belge_yolu)
                    if not basarili:
                        self.show_error(mesaj)
                else:
                    self.show_error("Bu işlemde belge bulunmamaktadır!")
                return
        
        self.show_error("İşlem bulunamadı!")

    # Modal açma fonksiyonları
    def open_yeni_hesap_modal(self) -> None:
        """Yeni hesap ekleme modal'ı"""
        self.open_hesap_modal(None)

    def open_gelir_modal(self, islem: Optional[FinansIslem] = None) -> None:
        """Gelir ekleme modal'ı"""
        self._open_islem_modal(islem, "Gelir")

    def open_gider_modal(self, islem: Optional[FinansIslem] = None) -> None:
        """Gider ekleme modal'ı"""
        self._open_islem_modal(islem, "Gider")

    def open_transfer_modal(self, islem: Optional[FinansIslem] = None) -> None:
        """Transfer ekleme modal'ı"""
        self._open_islem_modal(islem, "Transfer")

    def open_hesap_modal(self, hesap: Optional[Hesap] = None) -> None:
        """Hesap ekleme/düzenleme modal'ı"""
        self._open_hesap_modal(hesap)

    def _open_hesap_modal(self, hesap: Optional[Hesap] = None) -> None:
        """Hesap modalını aç"""
        # Modal pencere
        modal = ctk.CTkToplevel(self.frame)
        modal.title("Yeni Hesap Ekle" if hesap is None else "Hesap Düzenle")
        modal.resizable(False, False)
        
        # Sabit konumlandırma (ekran ortasında)
        modal.geometry("450x500+475+175")
        modal.transient(self.parent)
        modal.lift()
        modal.focus_force()

        # Ana frame
        main_frame = ctk.CTkFrame(modal, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text="Yeni Hesap Ekle" if hesap is None else "Hesap Düzenle",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(20, 30))

        # Form alanı
        form_frame = ctk.CTkScrollableFrame(main_frame, fg_color=self.colors["background"])
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Hesap Adı
        ad_label = ctk.CTkLabel(form_frame, text="Hesap Adı:", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        ad_label.pack(anchor="w", padx=20, pady=(20, 5))

        ad_entry = ctk.CTkEntry(form_frame, placeholder_text="Örn: Banka Hesabı")
        ad_entry.pack(fill="x", padx=20, pady=(0, 15))
        if hesap:
            ad_entry.insert(0, hesap.ad)

        # Hesap Türü
        tur_label = ctk.CTkLabel(form_frame, text="Hesap Türü:", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        tur_label.pack(anchor="w", padx=20, pady=(0, 5))

        tur_combo = ctk.CTkComboBox(
            form_frame,
            values=["Banka", "Kasa", "Cüzdan", "Tasarruf", "Diğer"],
            font=ctk.CTkFont(size=12),
            height=35
        )
        tur_combo.pack(fill="x", padx=20, pady=(0, 15))
        if hesap:
            tur_combo.set(hesap.tur)
        else:
            tur_combo.set("Banka")

        # Bakiye
        bakiye_label = ctk.CTkLabel(form_frame, text="Bakiye:", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        bakiye_label.pack(anchor="w", padx=20, pady=(0, 5))

        bakiye_entry = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        bakiye_entry.pack(fill="x", padx=20, pady=(0, 15))
        if hesap:
            bakiye_entry.insert(0, str(hesap.bakiye or 0))
        else:
            bakiye_entry.insert(0, "0.00")

        # Açıklama
        aciklama_label = ctk.CTkLabel(form_frame, text="Açıklama (Opsiyonel):", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        aciklama_label.pack(anchor="w", padx=20, pady=(0, 5))

        aciklama_textbox = ctk.CTkTextbox(form_frame, height=80, font=ctk.CTkFont(size=11))
        aciklama_textbox.pack(fill="x", padx=20, pady=(0, 20))
        if hesap and hasattr(hesap, 'aciklama') and hesap.aciklama:
            aciklama_textbox.insert("1.0", hesap.aciklama)

        # Butonlar
        button_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # İptal butonu
        cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ İptal",
            command=modal.destroy,
            fg_color=self.colors["text_secondary"],
            hover_color=self.colors["border"],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        cancel_button.pack(side="left", padx=(0, 10))

        # Kaydet butonu
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Kaydet",
            command=lambda: self.save_hesap(
                modal, hesap,
                ad_entry.get(),
                tur_combo.get(),
                bakiye_entry.get(),
                aciklama_textbox.get("1.0", "end").strip()
            ),
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_button.pack(side="right")

    def _open_islem_modal(self, islem: Optional[FinansIslem] = None, islem_turu: str = "Gelir") -> None:
        """İşlemler tablosu başlıklarına uygun modal"""
        # Düzenleme modunu ayarla
        self.duzenleme_modu = islem is not None
        self.hedef_hesap_combo = None  # Modal için hedef hesap combo

        # Modal başlığı ve renklerini belirle
        if islem_turu == "Gelir":
            modal_title = "💰 Yeni Gelir Ekle" if not self.duzenleme_modu else "💰 Gelir Düzenle"
            title_color = self.colors["success"]
            button_color = self.colors["success"]
        elif islem_turu == "Gider":
            modal_title = "💸 Yeni Gider Ekle" if not self.duzenleme_modu else "💸 Gider Düzenle"
            title_color = self.colors["error"]
            button_color = self.colors["error"]
        else:  # Transfer
            modal_title = "🔄 Yeni Transfer Ekle" if not self.duzenleme_modu else "🔄 Transfer Düzenle"
            title_color = self.colors["primary"]
            button_color = self.colors["primary"]

        # Modal pencere
        modal = ctk.CTkToplevel(self.frame)
        modal.title(modal_title)
        modal.resizable(False, False)
        
        # Sabit konumlandırma (ekran ortasında)
        modal.geometry("450x550+475+175")
        modal.transient(self.parent)
        modal.lift()
        # modal.focus_force()  # Removed to prevent TclError with scrollable frames

        # Ana frame
        main_frame = ctk.CTkFrame(modal, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text=modal_title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=title_color
        )
        title_label.pack(pady=(20, 30))

        # Form alanı - Scrollable frame ile aşağı kaydırma desteği
        form_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=self.colors["background"],
            height=350  # Daha fazla içerik için artırılmış yükseklik
        )
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Tablo sütunlarına göre alanlar
        # Tarih
        tarih_label = ctk.CTkLabel(form_frame, text="Tarih:", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        tarih_label.pack(anchor="w", padx=20, pady=(20, 5))

        tarih_frame = ctk.CTkFrame(form_frame, fg_color=self.colors["surface"], height=35)
        tarih_frame.pack(fill="x", padx=20, pady=(0, 15))
        tarih_frame.pack_propagate(False)

        tarih_entry = ctk.CTkEntry(tarih_frame, placeholder_text="GG.AA.YYYY", border_width=0, fg_color="transparent")
        tarih_entry.pack(side="left", fill="x", expand=True, padx=10)

        # Bugün butonu
        bugun_btn = ctk.CTkButton(
            tarih_frame,
            text="📅 Bugün",
            width=80,
            height=25,
            font=ctk.CTkFont(size=10),
            command=lambda: tarih_entry.delete(0, tk.END) or tarih_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        )
        bugun_btn.pack(side="right", padx=(5, 10))

        # Düzenleme ise mevcut tarihi, değilse bugünün tarihini varsayılan yap
        if islem and islem.tarih:
            tarih_entry.insert(0, islem.tarih.strftime("%d.%m.%Y"))
        else:
            tarih_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Ana kategori
        ana_kategori_label = ctk.CTkLabel(form_frame, text="Ana Kategori:", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])

        ana_kategori_options = []
        if islem_turu == "Gelir":
            ana_kategori_options = [kat.name for kat in self.ana_kategoriler if hasattr(kat, 'tip') and kat.tip == "gelir"]
        elif islem_turu == "Gider":
            ana_kategori_options = [kat.name for kat in self.ana_kategoriler if hasattr(kat, 'tip') and kat.tip == "gider"]

        ana_kategori_combo: ctk.CTkComboBox = ctk.CTkComboBox(
            form_frame,
            values=["Seçiniz"] + (ana_kategori_options if ana_kategori_options else []) if ana_kategori_options else ["Kategori bulunamadı"],
            font=ctk.CTkFont(size=12),
            height=35,
            command=lambda selected: self.update_alt_kategoriler(modal, ana_kategori_combo, alt_kategori_combo, selected)
        )

        # Transfer için kategori alanlarını gösterme
        if islem_turu != "Transfer":
            ana_kategori_label.pack(anchor="w", padx=20, pady=(0, 5))
            ana_kategori_combo.pack(fill="x", padx=20, pady=(0, 15))

            # Düzenleme ise mevcut kategoriyi, yeni işlem ise "Seçiniz" seç
            mevcut_ana_kat = None
            if islem:
                if hasattr(islem, 'kategori') and islem.kategori and islem.kategori.ana_kategori:
                    mevcut_ana_kat = islem.kategori.ana_kategori.name
                elif hasattr(islem, 'ana_kategori_text') and islem.ana_kategori_text:
                        mevcut_ana_kat = islem.ana_kategori_text
                
                if mevcut_ana_kat and mevcut_ana_kat in ana_kategori_options:
                    ana_kategori_combo.set(mevcut_ana_kat)
                else:
                    ana_kategori_combo.set("Seçiniz")
            else:
                # Yeni işlem eklerken "Seçiniz" göster
                ana_kategori_combo.set("Seçiniz")

        # Alt kategori
        alt_kategori_label = ctk.CTkLabel(form_frame, text="Alt Kategori (Opsiyonel):", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])

        # Alt kategoriler başlangıçta boş
        alt_kategori_options: List[str] = []

        alt_kategori_combo: ctk.CTkComboBox = ctk.CTkComboBox(
        form_frame,
        values=["Seçiniz"] + (alt_kategori_options if alt_kategori_options else []),
        font=ctk.CTkFont(size=12),
        height=35
        )

        # Transfer için alt kategori alanını gösterme
        if islem_turu != "Transfer":
            alt_kategori_label.pack(anchor="w", padx=20, pady=(0, 5))
            alt_kategori_combo.pack(fill="x", padx=20, pady=(0, 15))
            
            # Düzenleme modu ise mevcut alt kategoriyi seç, aksi takdirde "Seçiniz"
            if islem and hasattr(islem, 'kategori') and islem.kategori:
                alt_kategori_combo.set(islem.kategori.name)
            else:
                alt_kategori_combo.set("Seçiniz")

        # Hedef hesap (sadece transfer için)
        hedef_hesap_label = ctk.CTkLabel(form_frame, text="Hedef Hesap:", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])

        hedef_hesap_options = [f"{h.ad} ({h.tur})" for h in self.aktif_hesaplar]
        if not hedef_hesap_options:
            hedef_hesap_options = ["Aktif hesap bulunamadı"]
        else:
            # Transfer modalında hedef hesap için de "Seçiniz" seçeneğini ekle
            if islem_turu == "Transfer":
                hedef_hesap_options.insert(0, "Seçiniz")

        hedef_hesap_combo = ctk.CTkComboBox(
            form_frame,
            values=hedef_hesap_options,
            font=ctk.CTkFont(size=12),
            height=35
        )

        # Hesap (transfer için kaynak hesap)
        hesap_label = ctk.CTkLabel(form_frame, text="Hesap:", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        hesap_label.pack(anchor="w", padx=20, pady=(0, 5))

        hesap_options = [f"{h.ad} ({h.tur})" for h in self.aktif_hesaplar]
        if not hesap_options:
            hesap_options = ["Aktif hesap bulunamadı - Önce hesap ekleyin"]
        else:
            # Tüm modalarda "Seçiniz" seçeneğini ekle
            hesap_options.insert(0, "Seçiniz")

        hesap_combo = ctk.CTkComboBox(
            form_frame,
            values=hesap_options,
            font=ctk.CTkFont(size=12),
            height=35
        )
        hesap_combo.pack(fill="x", padx=20, pady=(0, 15))

        # Hesap seçimini belirle - değişken olarak saklayalım callback için
        secilen_hesap_value = None
        if islem and hasattr(islem, 'hesap') and islem.hesap:
            # Düzenleme modunda mevcut hesabı seç
            mevcut_hesap = f"{islem.hesap.ad} ({islem.hesap.tur})"
            if mevcut_hesap in hesap_options:
                secilen_hesap_value = mevcut_hesap
            elif hesap_options and hesap_options[0] != "Aktif hesap bulunamadı - Önce hesap ekleyin":
                secilen_hesap_value = hesap_options[0] if hesap_options[0] != "Seçiniz" else "Seçiniz"
        elif islem_turu == "Transfer":
            # Transfer modal'ında varsayılan hesap varsa seç, yoksa "Seçiniz"
            varsayilan_hesap = self.hesap_controller.get_varsayilan_hesap()
            if varsayilan_hesap:
                varsayilan_secenek = f"{varsayilan_hesap.ad} ({varsayilan_hesap.tur})"
                if varsayilan_secenek in hesap_options:
                    secilen_hesap_value = varsayilan_secenek
                else:
                    secilen_hesap_value = "Seçiniz"
            else:
                secilen_hesap_value = "Seçiniz"
        elif hesap_options and hesap_options[0] != "Aktif hesap bulunamadı - Önce hesap ekleyin":
            # Gelir/Gider modal'ında varsayılan hesap varsa seç, yoksa "Seçiniz" göster
            varsayilan_hesap = self.hesap_controller.get_varsayilan_hesap()
            if varsayilan_hesap:
                varsayilan_secenek = f"{varsayilan_hesap.ad} ({varsayilan_hesap.tur})"
                if varsayilan_secenek in hesap_options:
                    secilen_hesap_value = varsayilan_secenek
                else:
                    # Varsayılan hesap bulunamazsa "Seçiniz" seç
                    secilen_hesap_value = "Seçiniz"
            else:
                # Varsayılan hesap yoksa "Seçiniz" seç
                secilen_hesap_value = "Seçiniz"
        
        # Varsayılan değer set etmeden önce combo'yu ayarla, sonra callback'i tetikle
        if secilen_hesap_value:
            hesap_combo.set(secilen_hesap_value)

        # Hesap seçimi değiştiğinde para birimini güncelle
        def on_hesap_change(choice: str) -> None:
            if choice and choice != "Aktif hesap bulunamadı - Önce hesap ekleyin":
                # Hesap adını çıkar
                hesap_ad = choice.split(" (")[0]
                secilen_hesap = next((h for h in self.aktif_hesaplar if h.ad == hesap_ad), None)
                if secilen_hesap and hasattr(secilen_hesap, 'para_birimi'):
                    self.tutar_label.configure(text=f"Tutar ({secilen_hesap.para_birimi}):")
                else:
                    self.tutar_label.configure(text="Tutar (₺):")
            else:
                self.tutar_label.configure(text="Tutar (₺):")
                
        hesap_combo.configure(command=on_hesap_change)
        
        # Hedef hesap (sadece transfer için)
        if islem_turu == "Transfer":
            hedef_hesap_label.pack(anchor="w", padx=20, pady=(0, 5))
            hedef_hesap_combo.pack(fill="x", padx=20, pady=(0, 15))
            
            # Hedef hesap combo'yu instance variable olarak sakla
            self.hedef_hesap_combo = hedef_hesap_combo
            
            # Varsayılan hedef hesap seçimi
            if hedef_hesap_options and hedef_hesap_options[0] != "Aktif hesap bulunamadı":
                hedef_hesap_combo.set(hedef_hesap_options[0])

        # Tutar
        self.tutar_label = ctk.CTkLabel(form_frame, text="Tutar (₺):", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        self.tutar_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        tutar_entry = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        tutar_entry.pack(fill="x", padx=20, pady=(0, 15))
        if islem:
            tutar_entry.insert(0, str(islem.tutar or 0))

        # Açıklama
        aciklama_label = ctk.CTkLabel(form_frame, text="Açıklama (Opsiyonel):", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        aciklama_label.pack(anchor="w", padx=20, pady=(15, 5))

        aciklama_textbox = ctk.CTkTextbox(
            form_frame,
            height=60,
            font=ctk.CTkFont(size=11)
        )
        aciklama_textbox.pack(fill="x", padx=20, pady=(0, 20))

        # Düzenleme ise mevcut açıklamayı doldur
        if islem and hasattr(islem, 'aciklama') and islem.aciklama:
            aciklama_textbox.insert("1.0", islem.aciklama)

        # Hesap seçimi yapıldıktan sonra callback'i manuel çağır
        if secilen_hesap_value and secilen_hesap_value != "Seçiniz":
            on_hesap_change(secilen_hesap_value)

        # Belge ekleme bölümü
        belge_label = ctk.CTkLabel(form_frame, text="📎 Belge (Opsiyonel):", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        belge_label.pack(anchor="w", padx=20, pady=(10, 5))

        # Belge durumu göstergesi
        self.belge_durumu_label = ctk.CTkLabel(
            form_frame, 
            text="Belge seçilmedi",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=10)
        )
        self.belge_durumu_label.pack(anchor="w", padx=20, pady=(0, 5))

        # Belge butonları
        belge_buttons_frame = ctk.CTkFrame(form_frame, fg_color=self.colors["background"])
        belge_buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Belge seç butonu
        belge_sec_btn = ctk.CTkButton(
            belge_buttons_frame,
            text="📁 Seç",
            command=lambda: self.sec_belge(),
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            height=30,
            width=100,
            font=ctk.CTkFont(size=10, weight="bold")
        )
        belge_sec_btn.pack(side="left", padx=(0, 10))

        # Belgeyi aç butonu
        self.belge_ac_btn = ctk.CTkButton(
            belge_buttons_frame,
            text="👁️ Aç",
            command=lambda: self.ac_secili_belge(),
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"],
            height=30,
            width=100,
            font=ctk.CTkFont(size=10, weight="bold"),
            state="disabled" if not self.secili_belge_yolu else "normal"
        )
        self.belge_ac_btn.pack(side="left")

        # Butonlar
        button_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # İptal butonu
        cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ İptal",
            command=modal.destroy,
            fg_color=self.colors["text_secondary"],
            hover_color=self.colors["border"],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        cancel_button.pack(side="left", padx=(0, 10))

        # Kaydet butonu
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Kaydet",
            command=lambda: self.validate_and_save_islem(
                modal, islem_turu, tarih_entry, ana_kategori_combo, alt_kategori_combo, 
                hesap_combo, hedef_hesap_combo, tutar_entry, aciklama_textbox
            ),
            fg_color=button_color,
            hover_color=self.colors["primary"],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_button.pack(side="right")

    def validate_and_save_islem(self, modal: ctk.CTkToplevel, islem_turu: str, tarih_entry: ctk.CTkEntry, ana_kategori_combo: ctk.CTkComboBox, alt_kategori_combo: ctk.CTkComboBox, 
                               hesap_combo: ctk.CTkComboBox, hedef_hesap_combo: ctk.CTkComboBox, tutar_entry: ctk.CTkEntry, aciklama_textbox: ctk.CTkTextbox) -> None:
        """İşlem kaydetmeden önce UI validasyonlarını yapar"""
        # Validate combobox selections
        if islem_turu != "Transfer":
            # For Gelir/Gider operations, validate ana_kategori and alt_kategori
            ana_kategori_value = ana_kategori_combo.get()
            if ana_kategori_value == "Seçiniz" or not ana_kategori_value or ana_kategori_value == "Kategori bulunamadı":
                result = UIValidator.validate_combobox(ana_kategori_combo, "Ana Kategori", parent=modal)
                if result is None:
                    return
                    
            alt_kategori_value = alt_kategori_combo.get()
            if alt_kategori_value == "Seçiniz" or not alt_kategori_value:
                result = UIValidator.validate_combobox(alt_kategori_combo, "Alt Kategori", parent=modal)
                if result is None:
                    return
        
        # For all operations, validate hesap
        hesap_value = hesap_combo.get()
        if hesap_value == "Seçiniz" or not hesap_value or hesap_value == "Aktif hesap bulunamadı - Önce hesap ekleyin":
            result = UIValidator.validate_combobox(hesap_combo, "Hesap", parent=modal)
            if result is None:
                return
                
        # For Transfer operations, validate hedef_hesap
        if islem_turu == "Transfer":
            hedef_hesap_value = hedef_hesap_combo.get()
            if hedef_hesap_value == "Seçiniz" or not hedef_hesap_value or hedef_hesap_value == "Aktif hesap bulunamadı":
                result = UIValidator.validate_combobox(hedef_hesap_combo, "Hedef Hesap", parent=modal)
                if result is None:
                    return

        # All validations passed, call save_islem
        self.save_islem(
            modal, islem_turu, tarih_entry.get(),
            ana_kategori_combo.get() if islem_turu != "Transfer" else "",
            alt_kategori_combo.get() if islem_turu != "Transfer" else "",
            hesap_combo.get(),
            tutar_entry.get(), aciklama_textbox.get("1.0", "end").strip()
        )
        return

    def update_alt_kategoriler(self, modal: ctk.CTkToplevel, ana_kategori_combo: ctk.CTkComboBox, alt_kategori_combo: ctk.CTkComboBox, selected_ana_kategori: str) -> None:
        """Ana kategori değiştiğinde alt kategorileri güncelle"""
        try:
            # "Seçiniz" seçilmişse alt kategorileri temizle
            if selected_ana_kategori == "Seçiniz":
                alt_kategori_combo.configure(values=["Seçiniz"])
                alt_kategori_combo.set("Seçiniz")
                return
            
            # Seçilen ana kategoriye ait alt kategorileri bul
            ana_kat = next((kat for kat in self.ana_kategoriler if kat.name == selected_ana_kategori), None)
            if ana_kat:
                alt_kategoriler = [alt.name for alt in ana_kat.alt_kategoriler if hasattr(alt, 'aktif') and alt.aktif]
                alt_kategori_combo.configure(values=["Seçiniz"] + alt_kategoriler)
                alt_kategori_combo.set("Seçiniz")
        except Exception as e:
            print(f"Alt kategoriler güncellenirken hata: {e}")


    def save_islem(self, modal: ctk.CTkToplevel, islem_turu: str, tarih: str, ana_kategori: str, alt_kategori: str, hesap: str, tutar: str, aciklama: str) -> None:
        """İşlemler tablosuna uygun işlemi kaydet - ErrorHandler ile"""
        with ErrorHandler(parent=modal, show_success_msg=False):
            # Validasyonlar
            if not tarih.strip():
                raise ValidationError(
                    "Tarih boş olamaz",
                    code="VAL_001"
                )

            if not tutar.strip():
                raise ValidationError(
                    "Tutar boş olamaz",
                    code="VAL_001"
                )

            if hesap == "Aktif hesap bulunamadı - Önce hesap ekleyin" or hesap == "Hesap Seçiniz" or hesap == "Seçiniz":
                raise ValidationError(
                    "Geçerli bir hesap seçilmelidir",
                    code="VAL_001"
                )
            
            # Transfer dışı işlemler için ana kategori kontrolü
            if islem_turu != "Transfer":
                if not ana_kategori or ana_kategori == "Seçiniz":
                    raise ValidationError(
                        "Ana kategori seçilmelidir",
                        code="VAL_001"
                    )

            # Tarih parse
            try:
                tarih_obj = datetime.strptime(tarih.strip(), "%d.%m.%Y")
            except ValueError:
                raise ValidationError(
                    "Tarih GG.AA.YYYY formatında olmalıdır",
                    code="VAL_006"
                )

            # Tutar parse
            try:
                tutar_val = float(tutar.strip().replace(',', '.'))
            except ValueError:
                raise ValidationError(
                    "Tutar geçerli bir sayı olmalıdır",
                    code="VAL_002"
                )

            if tutar_val <= 0:
                raise ValidationError(
                    "Tutar 0'dan büyük olmalıdır",
                    code="VAL_005"
                )

            # Transfer dışı işlemler için kategori kontrolü
            if islem_turu != "Transfer":
                if not ana_kategori or ana_kategori == "Kategori bulunamadı":
                    raise ValidationError(
                        "Ana kategori zorunludur",
                        code="VAL_001"
                    )

            # Transfer işlemleri için hedef hesap kontrolü
            hedef_hesap = None
            if islem_turu == "Transfer":
                # Check if hedef_hesap_combo is properly initialized
                if hasattr(self, 'hedef_hesap_combo') and self.hedef_hesap_combo is not None:
                    try:
                        hedef_hesap = self.hedef_hesap_combo.get()
                    except Exception:
                        raise ValidationError(
                            "Hedef hesap seçimi yapılamadı",
                            code="VAL_001"
                        )
                else:
                    raise ValidationError(
                        "Hedef hesap seçimi yapılamadı",
                        code="VAL_001"
                    )
            if islem_turu == "Transfer" and (not hedef_hesap or hedef_hesap == "Aktif hesap bulunamadı" or hedef_hesap == "Hesap Seçiniz" or hedef_hesap == "Seçiniz"):
                raise ValidationError(
                    "Hedef hesap seçilmelidir",
                    code="VAL_001"
                )

            # Hesap ID'sini al
            hesap_id = None
            if hesap and "(" in hesap:
                hesap_ad = hesap.split(" (")[0]
                secilen_hesap = next((h for h in self.aktif_hesaplar if h.ad == hesap_ad), None)
                if secilen_hesap:
                    hesap_id = secilen_hesap.id

            # Hedef hesap ID'sini al (transfer için)
            hedef_hesap_id = None
            if islem_turu == "Transfer" and hedef_hesap and "(" in hedef_hesap:
                hedef_hesap_ad = hedef_hesap.split(" (")[0]
                secilen_hedef_hesap = next((h for h in self.aktif_hesaplar if h.ad == hedef_hesap_ad), None)
                if secilen_hedef_hesap:
                    hedef_hesap_id = secilen_hedef_hesap.id

            # Transfer işlemleri için para birimi kontrolü
            if islem_turu == "Transfer" and hesap_id is not None and hedef_hesap_id is not None:
                # Kaynak ve hedef hesapları bul
                kaynak_hesap = next((h for h in self.aktif_hesaplar if h.id == hesap_id), None)
                hedef_hesap_obj = next((h for h in self.aktif_hesaplar if h.id == hedef_hesap_id), None)
                
                # Her iki hesap da varsa para birimi kontrolü yap
                if kaynak_hesap and hedef_hesap_obj:
                    kaynak_para_birimi = getattr(kaynak_hesap, 'para_birimi', '₺')
                    hedef_para_birimi = getattr(hedef_hesap_obj, 'para_birimi', '₺')
                    
                    if kaynak_para_birimi != hedef_para_birimi:
                        raise BusinessLogicError(
                            "Transfer işlemleri yalnızca aynı para birimine sahip hesaplar arasında yapılabilir",
                            code="BIZ_001"
                        )

            # Kategori ID'sini al
            kategori_id = None
            if islem_turu != "Transfer" and ana_kategori and alt_kategori and alt_kategori != "Alt kategori bulunamadı":
                # Ana kategoriyi bul
                ana_kat = next((k for k in self.ana_kategoriler if k.name == ana_kategori), None)
                if ana_kat:
                    # Alt kategoriyi bul
                    alt_kat = next((a for a in ana_kat.alt_kategoriler if a.name == alt_kategori), None)
                    if alt_kat:
                        kategori_id = alt_kat.id

            # Belge yolunu ekle
            belge_yolu = None
            if hasattr(self, 'secili_belge_yolu') and self.secili_belge_yolu:
                belge_yolu = self.secili_belge_yolu
            
            # İşlemi veritabanına kaydet
            data = {
                'tarih': tarih_obj,
                'tur': islem_turu,
                'tutar': tutar_val,
                'aciklama': aciklama.strip() if aciklama.strip() else None,
                'hesap_id': hesap_id,
                'hedef_hesap_id': hedef_hesap_id,
                'kategori_id': kategori_id,
                'ana_kategori_text': ana_kategori if not kategori_id else None,
                'belge_yolu': belge_yolu,
                'aktif': True
            }
            
            # Düzenleme modundaysak mevcut işlemi güncelle, değilse yeni işlem oluştur
            if hasattr(self, 'duzenleme_modu') and self.duzenleme_modu and hasattr(self, 'duzenlenen_islem_id') and self.duzenlenen_islem_id is not None:
                # Düzenleme yaparken hesap bakiyelerini doğru şekilde güncelle
                self.finans_controller.update_with_balance_adjustment(int(self.duzenlenen_islem_id), data)
                action = "güncellendi"
            else:
                # Yeni işlem oluştur (create metodu bakiye güncellemesini otomatik yapar)
                self.finans_controller.create(data)
                action = "eklendi"
            
            # Hesap para birimini al
            para_birimi = "₺"  # Varsayılan
            if hesap_id is not None:
                secilen_hesap = next((h for h in self.aktif_hesaplar if h.id == hesap_id), None)
                if secilen_hesap and hasattr(secilen_hesap, 'para_birimi'):
                    para_birimi = secilen_hesap.para_birimi
            
            show_success(parent=modal, title="Başarılı", message=f"{islem_turu} '{tutar_val:.2f} {para_birimi}' başarıyla {action}!")

            # Modal'ı kapat
            modal.destroy()

            # Listeleri yenile
            self.load_data()


    def open_islem_modal(self, islem: Optional[FinansIslem] = None, islem_turu: str = "Gelir") -> None:
        """Gelir/gider ekleme/düzenleme modal'ı"""
        # Verileri yeniden yükle (hesap/ana kategori değişiklikleri için)
        self.load_hesaplar()
        self.load_ana_kategoriler()

        # Modal pencere
        modal = ctk.CTkToplevel(self.frame)
        modal.title(f"Yeni {islem_turu} Ekle" if islem is None else f"{islem_turu} Düzenle")
        modal.geometry("600x500")
        modal.transient(self.parent)
        modal.lift()
        modal.focus_force()

        # Başlık
        title_text = f"Yeni {islem_turu} Ekle" if islem is None else f"{islem_turu} Düzenle"
        title_label = ctk.CTkLabel(
            modal,
            text=title_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["success"] if islem_turu == "Gelir" else self.colors["error"]
        )
        title_label.pack(pady=(20, 10))

        # Scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(modal, fg_color=self.colors["surface"])
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # İşlem tarihi
        tarih_label = ctk.CTkLabel(scrollable_frame, text="İşlem Tarihi:", text_color=self.colors["text"])
        tarih_label.pack(anchor="w", padx=20, pady=(20, 5))

        tarih_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="GG.AA.YYYY")
        tarih_entry.pack(fill="x", padx=20, pady=(0, 15))
        if islem and islem.tarih:
            tarih_entry.insert(0, islem.tarih.strftime("%d.%m.%Y"))
        else:
            tarih_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Ana Kategori ve Kategori - Transfer için gizle
        if islem_turu != "Transfer":
            # Ana Kategori
            ana_kategori_label = ctk.CTkLabel(scrollable_frame, text="Ana Kategori:", text_color=self.colors["text"])
            ana_kategori_label.pack(anchor="w", padx=20, pady=(0, 5))

            # Ana kategorileri veritabanından al
            ana_kategori_db_options = [k.name for k in self.ana_kategoriler]
            ana_kategori_options = ["Seçiniz"] + ana_kategori_db_options

            ana_kategori_combo = ctk.CTkComboBox(scrollable_frame, values=ana_kategori_options, command=self.on_ana_kategori_change)
            ana_kategori_combo.pack(fill="x", padx=20, pady=(0, 15))
            
            # Seçim yap
            if islem and islem.kategori and islem.kategori.ana_kategori:
                if islem.kategori.ana_kategori.name in ana_kategori_options:
                    ana_kategori_combo.set(islem.kategori.ana_kategori.name)
                else:
                    ana_kategori_combo.set("Seçiniz")
            else:
                ana_kategori_combo.set("Seçiniz")

            # Kategori
            kategori_label = ctk.CTkLabel(scrollable_frame, text="Kategori:", text_color=self.colors["text"])
            kategori_label.pack(anchor="w", padx=20, pady=(0, 5))

            # Seçilen ana kategoriye göre alt kategorileri göster
            selected_ana_kategori = ana_kategori_combo.get()
            kategori_options = []
            for k in self.ana_kategoriler:  # Changed from self.kategoriler to self.ana_kategoriler
                if k.name == selected_ana_kategori:  # Changed from k.ana_kategori to k.name
                    # Get alt categories for this ana kategori
                    kategori_options.extend([alt.name for alt in k.alt_kategoriler])  # Changed from k.ad to alt.name

            if not kategori_options:
                kategori_options = ["Kategori bulunamadı"]

            self.kategori_combo = ctk.CTkComboBox(scrollable_frame, values=kategori_options)
            self.kategori_combo.pack(fill="x", padx=20, pady=(0, 15))
            if kategori_options and kategori_options[0] != "Kategori bulunamadı":
                self.kategori_combo.set(kategori_options[0])
            elif islem and islem.kategori:
                if islem.kategori.name in kategori_options:
                    self.kategori_combo.set(islem.kategori.name)
        else:
            # Transfer için kategori değişkenlerini None yap
            ana_kategori_combo = None
            self.kategori_combo = None

        # Hesap
        hesap_label = ctk.CTkLabel(scrollable_frame, text="Hesap:", text_color=self.colors["text"])
        hesap_label.pack(anchor="w", padx=20, pady=(0, 5))

        hesap_options = [f"{h.ad} ({h.tur})" for h in self.aktif_hesaplar]
        print(f"DEBUG: aktif_hesaplar count: {len(self.aktif_hesaplar)}")
        print(f"DEBUG: hesap_options before: {hesap_options}")
        if not hesap_options:
            hesap_options = ["Aktif hesap bulunamadı - Önce hesap ekleyin"]
        else:
            # Hesaplar varsa, "Hesap Seçiniz" seçeneğini ekle
            hesap_options.insert(0, "Hesap Seçiniz")
        print(f"DEBUG: hesap_options after: {hesap_options}")

        hesap_combo = ctk.CTkComboBox(scrollable_frame, values=hesap_options)
        hesap_combo.pack(fill="x", padx=20, pady=(0, 15))
        hesap_combo.configure(values=hesap_options)
        print(f"DEBUG: combo values: {hesap_combo._values}")

        # Seçim yap
        if "Aktif hesap bulunamadı" in hesap_options[0]:
            hesap_combo.set(hesap_options[0])
        else:
            # Önce düzenleme için mevcut hesabı kontrol et
            if islem and islem.hesap:
                selected_hesap = f"{islem.hesap.ad} ({islem.hesap.tur})"
                if selected_hesap in hesap_options:
                    hesap_combo.set(selected_hesap)
                else:
                    # Yeni işlem için varsayılan hesabı kontrol et
                    varsayilan_hesap = self.hesap_controller.get_varsayilan_hesap()
                    if varsayilan_hesap:
                        # Varsayılan hesabı seç
                        varsayilan_secenek = f"{varsayilan_hesap.ad} ({varsayilan_hesap.tur})"
                        if varsayilan_secenek in hesap_options:
                            hesap_combo.set(varsayilan_secenek)
                        else:
                            hesap_combo.set("Hesap Seçiniz")
                    else:
                        # Varsayılan yoksa "Hesap Seçiniz" seçili
                        hesap_combo.set("Hesap Seçiniz")

        # Varsayılan yoksa "Hesap Seçiniz" seçili
        hesap_combo.set("Hesap Seçiniz")

        tutar_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="0.00")
        tutar_entry.pack(fill="x", padx=20, pady=(0, 15))
        if islem:
            tutar_entry.insert(0, str(islem.tutar or 0))

        # Hesap seçimi değiştiğinde para birimini güncelle
        def on_hesap_change(choice: str) -> None:
            if choice and choice != "Aktif hesap bulunamadı - Önce hesap ekleyin":
                # Hesap adını çıkar
                hesap_ad = choice.split(" (")[0]
                secilen_hesap = next((h for h in self.aktif_hesaplar if h.ad == hesap_ad), None)
                if secilen_hesap and hasattr(secilen_hesap, 'para_birimi'):
                    self.tutar_label.configure(text=f"Tutar ({secilen_hesap.para_birimi}):")
                else:
                    self.tutar_label.configure(text="Tutar (₺):")
            else:
                self.tutar_label.configure(text="Tutar (₺):")


        hesap_combo.configure(command=on_hesap_change)
        
        # Eğer düzenleme modundaysa ve hesap varsa para birimini ayarla
        if islem and islem.hesap:
            on_hesap_change(f"{islem.hesap.ad} ({islem.hesap.tur})")

        # Açıklama
        aciklama_label = ctk.CTkLabel(scrollable_frame, text="Açıklama (Opsiyonel):", text_color=self.colors["text"])
        aciklama_label.pack(anchor="w", padx=20, pady=(0, 5))

        aciklama_textbox = ctk.CTkTextbox(scrollable_frame, height=80)
        aciklama_textbox.pack(fill="x", padx=20, pady=(0, 20))
        if islem and islem.aciklama:
            aciklama_textbox.insert("1.0", islem.aciklama)

        # Butonlar
        button_frame = ctk.CTkFrame(modal, fg_color=self.colors["background"])
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # İptal butonu
        cancel_button = ctk.CTkButton(
            button_frame,
            text="İptal",
            command=modal.destroy,
            fg_color=self.colors["text_secondary"],
            hover_color=self.colors["border"]
        )
        cancel_button.pack(side="left", padx=(0, 10))

        # Kaydet butonu
        save_button = ctk.CTkButton(
            button_frame,
            text="Kaydet",
            command=lambda: self.save_islem(
                modal, islem_turu, tarih_entry.get(),
                ana_kategori_combo.get() if ana_kategori_combo else "",
                self.kategori_combo.get() if self.kategori_combo else "",
                hesap_combo.get(), tutar_entry.get(), aciklama_textbox.get("1.0", "end").strip()
            ),
            fg_color=self.colors["success"] if islem_turu == "Gelir" else (self.colors["error"] if islem_turu == "Gider" else self.colors["primary"]),
            hover_color=self.colors["primary"]
        )
        save_button.pack(side="right")

    def save_hesap(self, modal: ctk.CTkToplevel, existing_hesap: Optional[Hesap], ad: str, tur: str, bakiye: str, aciklama: Optional[str], para_birimi_text: Optional[str] = None) -> None:
        """Hesap'ı kaydet"""
        # Form validasyonu (string parametreler olarak geliyor)
        ad = ad.strip()
        
        try:
            # Hesap adı validasyonu
            Validator.validate_required(ad, "Hesap Adı")
            Validator.validate_string_length(ad, "Hesap Adı", 1, 100)
            
            # Hesap türü validasyonu
            if not tur or tur == "Seçiniz":
                show_error(parent=modal, title="Hata", message="Hesap türü seçilmelidir!")
                return
            
            # Bakiye validasyonu
            try:
                bakiye_val = float(bakiye.strip()) if bakiye.strip() else 0.0
            except ValueError:
                show_error(parent=modal, title="Hata", message="Bakiye geçerli bir sayı olmalıdır!")
                return
            
            Validator.validate_positive_number(bakiye_val, "Bakiye", allow_zero=True)
        
        except ValidationError as e:
            show_error(parent=modal, title="Hata", message=str(e.message))
            return

        aciklama = aciklama.strip() if aciklama else None

        # Para birimi her zaman Türk Lirası
        para_birimi = "₺"

        try:
            with ErrorHandler(parent=modal, show_success_msg=False):
                # Hesabı veritabanına kaydet
                if existing_hesap:
                    # Mevcut hesabı güncelle
                    data = {
                        'ad': ad,
                        'tur': tur,
                        'bakiye': bakiye_val,
                        'aciklama': aciklama if aciklama else None,
                        'para_birimi': para_birimi
                    }
                    self.hesap_controller.update(existing_hesap.id, data)
                    action = "güncellendi"
                else:
                    # Yeni hesap oluştur
                    data = {
                        'ad': ad,
                        'tur': tur,
                        'bakiye': bakiye_val,
                        'aciklama': aciklama if aciklama else None,
                        'aktif': True,
                        'varsayilan': False,
                        'para_birimi': para_birimi
                    }
                    self.hesap_controller.create(data)
                    action = "eklendi"

                # Modal'ı kapat SONRA mesaj göster
                modal.destroy()
                show_success(parent=self.parent, title="Başarılı", message=f"Hesap '{ad}' başarıyla {action}!")

                # Listeyi yenile
                self.load_data()

        except (ValidationError, DatabaseError, DuplicateError) as e:
            handle_exception(e, parent=modal)
        except Exception as e:
            handle_exception(e, parent=modal)

    def on_ana_kategori_change(self, selected_ana_kategori: str, islem_turu: Optional[str] = None) -> None:
        """Ana kategori değiştiğinde alt kategorileri güncelle"""
        try:
            # Seçilen ana kategoriye göre alt kategorileri bul
            kategori_options = []
            for k in self.ana_kategoriler:
                if k.name == selected_ana_kategori:
                    # Get alt categories for this ana kategori
                    # Filter by type if specified
                    for alt in k.alt_kategoriler:
                        if alt.aktif:  # Only show active categories
                            kategori_options.append(alt.name)

            if not kategori_options:
                kategori_options = ["Kategori bulunamadı"]

            # Kategori combo box'ını güncelle
            if hasattr(self, 'kategori_combo') and self.kategori_combo is not None:
                self.kategori_combo.configure(values=kategori_options)
                if kategori_options and kategori_options[0] != "Kategori bulunamadı":
                    self.kategori_combo.set(kategori_options[0])
        except Exception as e:
            # Hata olursa sessizce geç
            pass

    def setup_filtreleme_paneli(self, parent: ctk.CTkFrame) -> None:
        """Filtreleme panelini oluştur - Alt taraf, yatay layout"""
        # Dış frame
        filter_frame = ctk.CTkFrame(
            parent, 
            fg_color=self.colors["background"],
            border_width=2,
            border_color=self.colors["primary"]
        )
        filter_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        # Ana container - yatay layout
        content_frame = ctk.CTkFrame(filter_frame, fg_color=self.colors["background"])
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        filter_title = ctk.CTkLabel(
            content_frame,
            text="🔍 Filtreler",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["primary"]
        )
        filter_title.pack(anchor="w", pady=(0, 10))
        
        # Filtreler container - yatay düzen
        filters_container = ctk.CTkFrame(content_frame, fg_color=self.colors["background"])
        filters_container.pack(fill="x", pady=(0, 10))
        
        # İşlem türü filtresi
        tur_label = ctk.CTkLabel(
            filters_container, 
            text="İşlem Türü:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        tur_label.pack(side="left", padx=(0, 8))
        
        self.filter_tur_combo = ctk.CTkComboBox(
            filters_container,
            values=["Tümü", "Gelir", "Gider", "Transfer"],
            command=lambda v: self.uygula_filtreler(),
            width=130,
            height=28,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=10)
        )
        self.filter_tur_combo.set("Tümü")
        self.filter_tur_combo.pack(side="left", padx=(0, 20))
        
        # Hesap filtresi
        hesap_label = ctk.CTkLabel(
            filters_container,
            text="Hesap:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        hesap_label.pack(side="left", padx=(0, 8))
        
        self.filter_hesap_combo = ctk.CTkComboBox(
            filters_container,
            values=["Tümü"],
            command=lambda v: self.uygula_filtreler(),
            width=130,
            height=28,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=10)
        )
        self.filter_hesap_combo.set("Tümü")
        self.filter_hesap_combo.pack(side="left", padx=(0, 20))
        
        # Açıklama araması
        aciklama_label = ctk.CTkLabel(
            filters_container,
            text="Açıklama:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        aciklama_label.pack(side="left", padx=(0, 8))
        
        self.filter_aciklama_entry = ctk.CTkEntry(
            filters_container,
            placeholder_text="Ara...",
            width=130,
            height=28,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.filter_aciklama_entry.pack(side="left", padx=(0, 20))
        self.filter_aciklama_entry.bind("<KeyRelease>", lambda e: self.uygula_filtreler())
        
        # Tarih aralığı filtresi
        tarih_label = ctk.CTkLabel(
            filters_container,
            text="Tarih:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        tarih_label.pack(side="left", padx=(0, 8))
        
        # Başlangıç tarihi
        tarih_from_label = ctk.CTkLabel(
            filters_container,
            text="Başl.",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=9)
        )
        tarih_from_label.pack(side="left", padx=(0, 3))
        
        self.filter_tarih_from_entry = ctk.CTkEntry(
            filters_container,
            placeholder_text="GG.AA.YYYY",
            width=85,
            height=28,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.filter_tarih_from_entry.pack(side="left", padx=(0, 10))
        self.filter_tarih_from_entry.bind("<KeyRelease>", lambda e: self.uygula_filtreler())
        
        # Bitiş tarihi
        tarih_to_label = ctk.CTkLabel(
            filters_container,
            text="Bitiş",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=9)
        )
        tarih_to_label.pack(side="left", padx=(0, 3))
        
        self.filter_tarih_to_entry = ctk.CTkEntry(
            filters_container,
            placeholder_text="GG.AA.YYYY",
            width=85,
            height=28,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.filter_tarih_to_entry.pack(side="left", padx=(0, 15))
        self.filter_tarih_to_entry.bind("<KeyRelease>", lambda e: self.uygula_filtreler())
        
        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filters_container,
            text="🔄 Temizle",
            command=self.temizle_filtreler,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=10, weight="bold"),
            height=28,
            width=80,
            corner_radius=4
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def uygula_filtreler(self) -> None:
        """Seçili filtreleri tabloya uygula"""
        try:
            # Treeview'i temizle
            for item in self.islemler_tree.get_children():
                self.islemler_tree.delete(item)
            
            # Filtre değerlerini al
            filter_tur = self.filter_tur_combo.get()
            filter_hesap = self.filter_hesap_combo.get()
            filter_aciklama = self.filter_aciklama_entry.get().lower()
            
            # Tarih aralığı
            filter_tarih_from = None
            filter_tarih_to = None
            try:
                if self.filter_tarih_from_entry.get().strip():
                    filter_tarih_from = datetime.strptime(self.filter_tarih_from_entry.get().strip(), "%d.%m.%Y")
            except ValueError:
                pass
            
            try:
                if self.filter_tarih_to_entry.get().strip():
                    filter_tarih_to = datetime.strptime(self.filter_tarih_to_entry.get().strip(), "%d.%m.%Y")
            except ValueError:
                pass
            
            # Tüm işlemleri filtrele
            for islem_tur, islem in self.tum_islemler_verisi:
                # Tür filtresi
                if filter_tur != "Tümü" and islem_tur.capitalize() != filter_tur:
                    continue
                
                # Hesap filtresi
                hesap_adi = islem.hesap.ad if islem.hesap else ""
                if filter_hesap != "Tümü" and hesap_adi != filter_hesap:
                    continue
                
                # Açıklama filtresi
                aciklama = (islem.aciklama or "").lower()
                if filter_aciklama and filter_aciklama not in aciklama:
                    continue
                
                # Tarih filtresi
                if islem.tarih:
                    if filter_tarih_from and islem.tarih.date() < filter_tarih_from.date():
                        continue
                    if filter_tarih_to and islem.tarih.date() > filter_tarih_to.date():
                        continue
                elif filter_tarih_from or filter_tarih_to:
                    # Tarih filtesi aktif ama işlemde tarih yoksa geç
                    continue
                
                # İşlemi tabloya ekle
                tutar_gosterimi = f"{islem.tutar:.2f}"
                if islem.hesap and hasattr(islem.hesap, 'para_birimi'):
                    tutar_gosterimi = f"{islem.tutar:.2f} {islem.hesap.para_birimi}"
                
                # Belge göstergesi
                belge_gostergesi = "📎" if (hasattr(islem, 'belge_yolu') and islem.belge_yolu) else ""
                
                if islem_tur == 'gelir':
                    self.islemler_tree.insert("", "end", values=(
                        f"G{islem.id}",
                        "Gelir",
                        islem.tarih.strftime("%d.%m.%Y") if islem.tarih else "",
                        (islem.kategori.ana_kategori.name if islem.kategori and islem.kategori.ana_kategori else islem.ana_kategori_text or ""),
                        islem.kategori.name if islem.kategori else "",
                        islem.hesap.ad if islem.hesap else "",
                        tutar_gosterimi,
                        belge_gostergesi,
                        islem.aciklama or ""
                    ), tags=("gelir",))
                elif islem_tur == 'gider':
                    self.islemler_tree.insert("", "end", values=(
                        f"Gd{islem.id}",
                        "Gider",
                        islem.tarih.strftime("%d.%m.%Y") if islem.tarih else "",
                        (islem.kategori.ana_kategori.name if islem.kategori and islem.kategori.ana_kategori else islem.ana_kategori_text or ""),
                        islem.kategori.name if islem.kategori else "",
                        islem.hesap.ad if islem.hesap else "",
                        tutar_gosterimi,
                        belge_gostergesi,
                        islem.aciklama or ""
                    ), tags=("gider",))
                else:  # transfer
                    transfer_tutar = f"{islem.tutar:.2f}"
                    if islem.hesap and hasattr(islem.hesap, 'para_birimi'):
                        transfer_tutar = f"{islem.tutar:.2f} {islem.hesap.para_birimi}"
                    
                    self.islemler_tree.insert("", "end", values=(
                        f"T{islem.id}",
                        "Transfer",
                        islem.tarih.strftime("%d.%m.%Y") if islem.tarih else "",
                        "",
                        "",
                        f"{islem.hesap.ad if islem.hesap else ''} → {islem.hedef_hesap.ad if islem.hedef_hesap else ''}",
                        transfer_tutar,
                        belge_gostergesi,
                        islem.aciklama or ""
                    ), tags=("transfer",))
            
            # Renk kodlaması
            self.islemler_tree.tag_configure("gelir", background="#e8f5e8")
            self.islemler_tree.tag_configure("gider", background="#ffeaea")
            self.islemler_tree.tag_configure("transfer", background="#e8f0ff")
        except Exception as e:
            print(f"Filtreleme hatası: {e}")

    def temizle_filtreler(self) -> None:
        """Tüm filtreleri temizle ve tüm işlemleri göster"""
        self.filter_tur_combo.set("Tümü")
        self.filter_hesap_combo.set("Tümü")
        self.filter_aciklama_entry.delete(0, "end")
        self.filter_tarih_from_entry.delete(0, "end")
        self.filter_tarih_to_entry.delete(0, "end")
        self.uygula_filtreler()

    # Belge yönetimi metodları
    def sec_belge(self) -> None:
       """Belge seçme dialog'unu aç"""
       try:
           dosya_yolu = filedialog.askopenfilename(
               title="Belge Seçin",
               filetypes=[
                   ("Tüm Dosyalar", "*.*"),
                   ("PDF Dosyaları", "*.pdf"),
                   ("Resim Dosyaları", "*.jpg *.jpeg *.png"),
                   ("Word Dosyaları", "*.doc *.docx"),
                   ("Excel Dosyaları", "*.xls *.xlsx"),
                   ("Metin Dosyaları", "*.txt")
               ]
           )
           
           if dosya_yolu:
               # Belge kontrollerini yap
               basarili, mesaj, saklanan_yol = self.belge_controller.dosya_ekle(dosya_yolu, 0, "İşlem")
               
               if basarili:
                   # Seçili belge yolunu güncelle
                   self.secili_belge_yolu = saklanan_yol
                   
                   # UI'yi güncelle
                   dosya_adi = "Belge seçili değil"
                   if self.secili_belge_yolu is not None:
                       dosya_adi = self.belge_controller.dosya_adi_al(self.secili_belge_yolu)
                   if hasattr(self, 'belge_durumu_label'):
                       self.belge_durumu_label.configure(text=f"✓ Belge: {dosya_adi}")
                   
                   # Butonları aktif yap
                   if hasattr(self, 'belge_sil_btn'):
                       self.belge_sil_btn.configure(state="normal")
                   if hasattr(self, 'belge_ac_btn'):
                       self.belge_ac_btn.configure(state="normal")
                   
                   self.show_message("Belge başarıyla seçildi!")
               else:
                   self.show_error(mesaj)
       except Exception as e:
           self.show_error(f"Belge seçme hatası: {str(e)}")

    def sil_secili_belge(self) -> None:
       """Seçili belgeyi sil"""
       try:
           if not hasattr(self, 'secili_belge_yolu') or not self.secili_belge_yolu:
               self.show_error("Silinecek belge bulunamadı!")
               return
           
           if self.ask_yes_no("Seçili belge gerçekten silinsin mi?"):
               basarili, mesaj = self.belge_controller.dosya_sil(self.secili_belge_yolu)
               
               if basarili:
                   self.secili_belge_yolu = None
                   
                   # UI'yi güncelle
                   if hasattr(self, 'belge_durumu_label'):
                       self.belge_durumu_label.configure(text="Belge seçilmedi")
                   
                   # Butonları pasif yap
                   if hasattr(self, 'belge_sil_btn'):
                       self.belge_sil_btn.configure(state="disabled")
                   if hasattr(self, 'belge_ac_btn'):
                       self.belge_ac_btn.configure(state="disabled")
                   
                   self.show_message("Belge başarıyla silindi!")
               else:
                   self.show_error(mesaj)
       except Exception as e:
           self.show_error(f"Belge silme hatası: {str(e)}")

    def ac_secili_belge(self) -> None:
       """Seçili belgeyi aç"""
       try:
           if not hasattr(self, 'secili_belge_yolu') or not self.secili_belge_yolu:
               self.show_error("Açılacak belge bulunamadı!")
               return
           
           basarili, mesaj = self.belge_controller.dosya_ac(self.secili_belge_yolu)
           
           if not basarili:
               self.show_error(mesaj)
       except Exception as e:
           self.show_error(f"Belge açma hatası: {str(e)}")

