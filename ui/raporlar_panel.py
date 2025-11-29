"""
Raporlar paneli - Tüm İşlem Detayları, Bilanço, İcmal, Konut Mali Durumları, Boş Konut Listesi
"""

import customtkinter as ctk
from tkinter import ttk
from typing import List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from datetime import datetime

    from datetime import datetime

    from datetime import datetime

    from datetime import datetime

    from datetime import datetime

    from datetime import datetime as datetime_type

from ui.base_panel import BasePanel
from ui.error_handler import (
    ErrorHandler, handle_exception, show_error, show_success, show_warning
)
from controllers.finans_islem_controller import FinansIslemController
from controllers.hesap_controller import HesapController
from controllers.sakin_controller import SakinController
from controllers.daire_controller import DaireController
from controllers.aidat_controller import AidatIslemController
from controllers.kategori_yonetim_controller import KategoriYonetimController
from controllers.bos_konut_controller import BosKonutController
from models.base import Daire, Blok, Lojman, Sakin, FinansIslem
from models.exceptions import DatabaseError, InsufficientDataError
from database.config import get_db
from sqlalchemy.orm import joinedload
class RaporlarPanel(BasePanel):
    """Raporlar paneli
    
    Kapsamlı finansal ve operasyonel raporları sunmaktadır.
    5 rapor sekmesinden oluşur:
    - Tüm İşlem Detayları
    - Bilanço
    - İcmal
    - Konut Mali Durumları
    - Boş Konut Listesi
    
    Attributes:
        finans_controller (FinansIslemController): Finansal işlem denetleyicisi
        hesap_controller (HesapController): Hesap yönetim denetleyicisi
        sakin_controller (SakinController): Sakin yönetim denetleyicisi
        daire_controller (DaireController): Daire yönetim denetleyicisi
        aidat_controller (AidatIslemController): Aidat yönetim denetleyicisi
        kategori_controller (KategoriYonetimController): Kategori yönetim denetleyicisi
    """

    def __init__(self, parent: ctk.CTkFrame, colors: dict) -> None:
        self.finans_controller = FinansIslemController()
        self.hesap_controller = HesapController()
        self.sakin_controller = SakinController()
        self.daire_controller = DaireController()
        self.aidat_controller = AidatIslemController()
        self.kategori_controller = KategoriYonetimController()  # Add this for category management

        super().__init__(parent, "📊 Raporlar", colors)

    def setup_ui(self) -> None:
        """UI'yi oluştur"""
        # Ana container
        main_frame = ctk.CTkFrame(self.frame, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab kontrolü
        self.tabview = ctk.CTkTabview(main_frame, width=1000, height=600)
        self.tabview.pack(fill="both", expand=True, padx=0, pady=0)

        # Tab'ları oluştur
        self.tabview.add("Tüm İşlem Detayları")
        self.tabview.add("Bilanço")
        self.tabview.add("İcmal")
        self.tabview.add("Konut Mali Durumları")
        self.tabview.add("Boş Konut Listesi")

        # Tab içeriklerini oluştur
        self.setup_tum_islem_detaylari_tab()
        self.setup_bilanco_tab()
        self.setup_icmal_tab()
        self.setup_konut_mali_durumlari_tab()
        self.setup_bos_konut_listesi_tab()

    def setup_tum_islem_detaylari_tab(self) -> None:

        """Tüm İşlem Detayları tab'ı - Dönemsel filtreleme ile"""
        tab = self.tabview.tab("Tüm İşlem Detayları")

        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # ===== ÜST KISIM: DÖNEMSEL FİNANS ÖZETİ =====
        ozet_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"], border_width=1, border_color=self.colors["primary"])
        ozet_frame.pack(fill="x", padx=0, pady=(0, 8))

        # Dönem başlığı
        donem_baslik = ctk.CTkLabel(
            ozet_frame,
            text="Dönemsel Finans Özeti",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors["primary"]
        )
        donem_baslik.pack(anchor="w", padx=10, pady=(5, 5))

        # Özet istatistikleri container
        ozet_istatistik_frame = ctk.CTkFrame(ozet_frame, fg_color=self.colors["background"])
        ozet_istatistik_frame.pack(fill="x", padx=10, pady=(0, 5))

        # Dönem Toplam Gelir
        gelir_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="Gelir:",
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text"]
        )
        gelir_label.pack(side="left", padx=(0, 5))

        self.donem_toplam_gelir_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="0.00 ₺",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["success"]
        )
        self.donem_toplam_gelir_label.pack(side="left", padx=(0, 25))

        # Dönem Toplam Gider
        gider_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="Gider:",
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text"]
        )
        gider_label.pack(side="left", padx=(0, 5))

        self.donem_toplam_gider_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="0.00 ₺",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["error"]
        )
        self.donem_toplam_gider_label.pack(side="left", padx=(0, 25))

        # Dönem Net Bakiye
        bakiye_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="Net Bakiye:",
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text"]
        )
        bakiye_label.pack(side="left", padx=(0, 5))

        self.donem_net_bakiye_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="0.00 ₺",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["primary"]
        )
        self.donem_net_bakiye_label.pack(side="left")

        # ===== ORTADA: İŞLEMLER TABLOSU =====
        table_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"])
        table_frame.pack(fill="both", expand=True, padx=0, pady=(0, 8))

        # İşlemler tablosu
        self.islem_tree = ttk.Treeview(
            table_frame,
            columns=("id", "tarih", "aciklama", "ana_kategori", "alt_kategori", "hesap", "tutar", "tur"),
            show="headings",
            height=15
        )

        # Kolon başlıkları
        self.islem_tree.heading("id", text="ID")
        self.islem_tree.heading("tarih", text="Tarih")
        self.islem_tree.heading("aciklama", text="Açıklama")
        self.islem_tree.heading("ana_kategori", text="Ana Kat.")
        self.islem_tree.heading("alt_kategori", text="Alt Kat.")
        self.islem_tree.heading("hesap", text="Hesap")
        self.islem_tree.heading("tutar", text="Tutar")
        self.islem_tree.heading("tur", text="Tür")

        # Kolon genişlikleri (kompakt)
        self.islem_tree.column("id", width=35, anchor="center")
        self.islem_tree.column("tarih", width=80, anchor="center")
        self.islem_tree.column("aciklama", width=120, anchor="center")
        self.islem_tree.column("ana_kategori", width=80, anchor="center")
        self.islem_tree.column("alt_kategori", width=80, anchor="center")
        self.islem_tree.column("hesap", width=100, anchor="center")
        self.islem_tree.column("tutar", width=80, anchor="center")
        self.islem_tree.column("tur", width=60, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.islem_tree.yview)
        self.islem_tree.configure(yscrollcommand=scrollbar.set)

        self.islem_tree.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        scrollbar.pack(side="right", fill="y", pady=0)

        # ===== ALT KISIM: FİLTRELEME SEÇENEKLERİ =====
        self.setup_tum_islem_filtreleme_paneli(main_frame)

        # Verileri yükle (UI tamamen kurulduktan sonra)
        # after() ile schedule yaparak combo box'lar ready hale gelsinde çalışacak
        tab.after(100, self.load_tum_islem_detaylari)

    def setup_bilanco_tab(self) -> None:
        """Bilanço tab'ı"""
        tab = self.tabview.tab("Bilanço")

        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # ===== ÜST KISIM: DÖNEM ÖZET İSTATİSTİKLERİ =====
        ozet_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"], border_width=1, border_color=self.colors["primary"])
        ozet_frame.pack(fill="x", padx=0, pady=(0, 8))

        # Başlık
        ozet_baslik = ctk.CTkLabel(
            ozet_frame,
            text="Dönem Özeti",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors["primary"]
        )
        ozet_baslik.pack(anchor="w", padx=10, pady=(5, 5))

        # Özet istatistikleri
        ozet_istatistik_frame = ctk.CTkFrame(ozet_frame, fg_color=self.colors["background"])
        ozet_istatistik_frame.pack(fill="x", padx=10, pady=(0, 5))

        # Önceki Dönem Bakiye
        onceki_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="Önceki Dönem Bakiye:",
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text"]
        )
        onceki_label.pack(side="left", padx=(0, 5))

        self.bilanco_onceki_bakiye_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="0.00 ₺",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["primary"]
        )
        self.bilanco_onceki_bakiye_label.pack(side="left", padx=(0, 30))

        # Dönem İçi Toplam Gelir
        gelir_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="Dönem İçi Toplam Gelir:",
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text"]
        )
        gelir_label.pack(side="left", padx=(0, 5))

        self.bilanco_donem_gelir_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="0.00 ₺",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["success"]
        )
        self.bilanco_donem_gelir_label.pack(side="left", padx=(0, 30))

        # Dönem İçi Toplam Gider
        gider_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="Dönem İçi Toplam Gider:",
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text"]
        )
        gider_label.pack(side="left", padx=(0, 5))

        self.bilanco_donem_gider_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="0.00 ₺",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["error"]
        )
        self.bilanco_donem_gider_label.pack(side="left", padx=(0, 30))

        # Dönem Sonu Bakiye
        son_bakiye_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="Dönem Sonu Bakiye:",
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text"]
        )
        son_bakiye_label.pack(side="left", padx=(0, 5))

        self.bilanco_son_bakiye_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="0.00 ₺",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["primary"]
        )
        self.bilanco_son_bakiye_label.pack(side="left")

        # ===== ORTA KISIM: DETAY TABLOSU =====
        table_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"])
        table_frame.pack(fill="both", expand=True, padx=0, pady=(0, 8))

        # Bilanço detay tablosu (tek tablo, tür ile ayır)
        self.bilanco_tree = ttk.Treeview(
            table_frame,
            columns=("tur", "kategori", "tutar"),
            show="headings",
            height=15
        )
        
        # Kolon başlıkları
        self.bilanco_tree.heading("tur", text="Tür")
        self.bilanco_tree.heading("kategori", text="Kategori")
        self.bilanco_tree.heading("tutar", text="Tutar")
        
        # Kolon genişlikleri
        self.bilanco_tree.column("tur", width=80, anchor="center")
        self.bilanco_tree.column("kategori", width=200, anchor="center")
        self.bilanco_tree.column("tutar", width=150, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.bilanco_tree.yview)
        self.bilanco_tree.configure(yscrollcommand=scrollbar.set)
        
        self.bilanco_tree.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        scrollbar.pack(side="right", fill="y", pady=0)

        # Renk kodlaması
        self.bilanco_tree.tag_configure("gelir", background="#e8f5e8")
        self.bilanco_tree.tag_configure("gider", background="#ffeaea")

        # ===== ALT KISIM: FİLTRELEME =====
        self.setup_bilanco_filtreleme_paneli(main_frame)

        # Verileri yükle
        tab.after(100, self.load_bilanco)

    def setup_icmal_tab(self) -> None:
        """İcmal tab'ı"""
        tab = self.tabview.tab("İcmal")
        
        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ===== ÜST KISIM: GİDER TOPLAMI (SAĞDA) =====
        ozet_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"], border_width=1, border_color=self.colors["primary"])
        ozet_frame.pack(fill="x", padx=0, pady=(0, 8))
        
        # Özet başlık
        ozet_baslik = ctk.CTkLabel(
            ozet_frame,
            text="Giderler Özeti",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors["primary"]
        )
        ozet_baslik.pack(anchor="w", padx=10, pady=(5, 5))
        
        # Özet istatistikleri container
        ozet_istatistik_frame = ctk.CTkFrame(ozet_frame, fg_color=self.colors["background"])
        ozet_istatistik_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        # Gider Toplamı: [amount] şeklinde sağ tarafta
        self.icmal_gider_toplam_label = ctk.CTkLabel(
            ozet_istatistik_frame,
            text="Gider Toplamı: 0.00 ₺",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["error"]
        )
        self.icmal_gider_toplam_label.pack(side="right")
        
        # ===== ORTA KISIM: DETAY TABLOSU =====
        table_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"])
        table_frame.pack(fill="both", expand=True, padx=0, pady=(0, 8))
        
        # İcmal detay tablosu
        self.icmal_tree = ttk.Treeview(
            table_frame,
            columns=("sira_no", "gider_turu", "gider_turu_ayrinti", "tutar", "aciklama", "tutar_toplami"),
            show="headings",
            height=15
        )
        
        # Kolon başlıkları
        self.icmal_tree.heading("sira_no", text="Sıra No")
        self.icmal_tree.heading("gider_turu", text="Gider Türü")
        self.icmal_tree.heading("gider_turu_ayrinti", text="Gider Türü Ayrıntısı")
        self.icmal_tree.heading("tutar", text="Tutar")
        self.icmal_tree.heading("aciklama", text="Açıklama")
        self.icmal_tree.heading("tutar_toplami", text="Tutar Toplamı")
        
        # Kolon genişlikleri
        self.icmal_tree.column("sira_no", width=50, anchor="center")
        self.icmal_tree.column("gider_turu", width=120, anchor="center")
        self.icmal_tree.column("gider_turu_ayrinti", width=150, anchor="center")
        self.icmal_tree.column("tutar", width=80, anchor="center")
        self.icmal_tree.column("aciklama", width=200, anchor="center")
        self.icmal_tree.column("tutar_toplami", width=100, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.icmal_tree.yview)
        self.icmal_tree.configure(yscrollcommand=scrollbar.set)
        
        self.icmal_tree.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        scrollbar.pack(side="right", fill="y", pady=0)
        
        # Treeview stilini ayarla (ızgara çizgileri için)
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 9, 'bold'))
        # Izgara çizgilerini etkinleştir
        style.configure("Treeview", background="white", fieldbackground="white", foreground="black")
        style.map("Treeview", background=[("selected", "#3475b3")])
        # Yatay ve dikey çizgileri göster
        self.icmal_tree.configure(style="Treeview")
        
        # ===== ALT KISIM: FİLTRELEME =====
        self.setup_icmal_filtreleme_paneli(main_frame)
        
        # Verileri yükle
        tab.after(100, self.load_icmal)

    def setup_icmal_filtreleme_paneli(self, parent: ctk.CTkFrame) -> None:
        """İcmal sekmesi için filtreleme paneli"""
        filter_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors["background"],
            border_width=1,
            border_color=self.colors["primary"]
        )
        filter_frame.pack(fill="x", padx=0, pady=(0, 0))
        
        # Başlık
        filter_title = ctk.CTkLabel(
            filter_frame,
            text="Filtre",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["primary"]
        )
        filter_title.pack(anchor="w", padx=8, pady=(3, 3))
        
        # Filtre container
        filter_content = ctk.CTkFrame(filter_frame, fg_color=self.colors["background"])
        filter_content.pack(fill="x", padx=8, pady=(0, 5))
        
        # Filtre türü seçimi (Yıllık/Aylık)
        filtre_tur_label = ctk.CTkLabel(
            filter_content,
            text="Tür:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        filtre_tur_label.pack(side="left", padx=(0, 5))
        
        from datetime import datetime
        
        self.icmal_filtre_tur_combo = ctk.CTkComboBox(
            filter_content,
            values=["Aylık", "Yıllık"],
            command=self.on_icmal_filtre_tur_change,
            width=70,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.icmal_filtre_tur_combo.set("Aylık")
        self.icmal_filtre_tur_combo.pack(side="left", padx=(0, 15))
        
        # Yıl seçimi - Veritabanındaki yıllardan dinamik olarak oluştur
        yil_label = ctk.CTkLabel(
            filter_content,
            text="Yıl:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        yil_label.pack(side="left", padx=(0, 5))
        
        # Veritabanından kullanılabilir yılları al
        yillar = self.get_veritabani_yillari()
        
        self.icmal_yil_combo = ctk.CTkComboBox(
            filter_content,
            values=yillar,
            command=self.on_icmal_filtre_change,
            width=65,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        
        # En yeni yılı seç
        if yillar:
            self.icmal_yil_combo.set(yillar[-1])  # Son yıl (en yeni)
        else:
            self.icmal_yil_combo.set(str(datetime.now().year))
        
        self.icmal_yil_combo.pack(side="left", padx=(0, 15))
        
        # Ay seçimi (başlangıçta görünür)
        ay_label = ctk.CTkLabel(
            filter_content,
            text="Ay:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        ay_label.pack(side="left", padx=(0, 5))
        
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.icmal_ay_combo = ctk.CTkComboBox(
            filter_content,
            values=aylar,
            command=self.on_icmal_filtre_change,
            width=75,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.icmal_ay_combo.set(aylar[datetime.now().month - 1])
        self.icmal_ay_combo.pack(side="left", padx=(0, 15))
        
        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filter_content,
            text="Temizle",
            command=self.temizle_icmal_filtreleri,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=8, weight="bold"),
            height=24,
            width=60,
            corner_radius=3
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def temizle_icmal_filtreleri(self) -> None:
        """İcmal filtreleri temizle"""
        from datetime import datetime
        self.icmal_filtre_tur_combo.set("Aylık")
        self.icmal_yil_combo.set(str(datetime.now().year))
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.icmal_ay_combo.set(aylar[datetime.now().month - 1])
        self.icmal_ay_combo.configure(state="normal")
        self.load_icmal()

    def load_icmal(self) -> None:
        """İcmal verilerini yükle"""
        try:
            # Treeview'i temizle
            for item in self.icmal_tree.get_children():
                self.icmal_tree.delete(item)
                
            # Filtre parametrelerini al
            from datetime import datetime
            
            # Combo box'ların varlığını kontrol et
            if not hasattr(self, 'icmal_filtre_tur_combo') or self.icmal_filtre_tur_combo is None:
                # İlk çağrıda combo box'lar henüz oluşturulmamış, varsayılan değerleri kullan
                filtre_tur = "Aylık"
                yil = datetime.now().year
                ay = datetime.now().month
            else:
                filtre_tur = self.icmal_filtre_tur_combo.get()  # "Aylık" veya "Yıllık"
                yil = int(self.icmal_yil_combo.get())
                
                # Ayı sayıya çevir (Ocak=1, Şubat=2, ...)
                aylar_dict = {
                    "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4,
                    "Mayıs": 5, "Haziran": 6, "Temmuz": 7, "Ağustos": 8,
                    "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12
                }
                ay_text = self.icmal_ay_combo.get()
                ay = aylar_dict.get(ay_text, datetime.now().month)
                
            # Giderleri al ve filtrele
            giderler = self.finans_controller.get_giderler()
            
            # Ana kategorilere göre grupla ve topla
            ana_kategori_toplamlar: dict = {}  # {ana_kategori: toplam_tutar}
            ana_kategori_para_birleri: dict = {}  # {ana_kategori: para_birimi}
            ana_kategori_alt_kategoriler: dict = {}  # {ana_kategori: {alt_kategori: [giderler]}}
            
            for gider in giderler:
                if self.uygula_tarih_filtresi(gider.tarih, filtre_tur, yil, ay):
                    # Ana kategori bilgilerini al
                    ana_kategori = "Tanımsız"
                    alt_kategori = "Tanımsız"
                    
                    if gider.kategori and gider.kategori.ana_kategori:
                        ana_kategori = gider.kategori.ana_kategori.name
                    
                    if gider.kategori:
                        alt_kategori = gider.kategori.name
                        
                    # Para birimini al
                    para_birimi = "₺"
                    if gider.hesap:
                        para_birimi = gider.hesap.para_birimi or "₺"
                    
                    # Ana kategori toplamlarını hesapla
                    if ana_kategori not in ana_kategori_toplamlar:
                        ana_kategori_toplamlar[ana_kategori] = 0.0
                        ana_kategori_para_birleri[ana_kategori] = para_birimi
                    ana_kategori_toplamlar[ana_kategori] += gider.tutar
                    
                    # Ana kategori alt kategorilerini grupla
                    if ana_kategori not in ana_kategori_alt_kategoriler:
                        ana_kategori_alt_kategoriler[ana_kategori] = {}
                    if alt_kategori not in ana_kategori_alt_kategoriler[ana_kategori]:
                        ana_kategori_alt_kategoriler[ana_kategori][alt_kategori] = []
                    ana_kategori_alt_kategoriler[ana_kategori][alt_kategori].append(gider)
            
            # Tabloya verileri görsel olarak gruplanmış şekilde ekle (renkli satırlarla)
            toplam_gider = 0.0
            genel_sira_no = 1  # Genel sıra numarası (her gider türü için 1 artar)
            
            # Ana kategorileri sıralı şekilde işle
            sorted_ana_kategoriler = sorted(ana_kategori_toplamlar.keys())
            
            # Renkli satır stilleri tanımla
            self.icmal_tree.tag_configure("even_group", background="#f0f0f0")
            self.icmal_tree.tag_configure("odd_group", background="#ffffff")
            
            for idx, ana_kategori in enumerate(sorted_ana_kategoriler):
                ana_kategori_toplam = ana_kategori_toplamlar[ana_kategori]
                
                # Bu ana kategoriye ait alt kategorileri işle
                alt_kategoriler = ana_kategori_alt_kategoriler.get(ana_kategori, {})
                
                # Her ana kategori için sıralı numara başlat
                ana_kategori_ilk_satir = True
                
                # Grup için etiket belirle (tek çift renk)
                group_tag = "even_group" if idx % 2 == 0 else "odd_group"
                
                for alt_kategori in sorted(alt_kategoriler.keys()):
                    alt_kategori_giderler = alt_kategoriler[alt_kategori]
                    
                    # Her gider için ayrı satır ekle
                    para_birimi = ana_kategori_para_birleri.get(ana_kategori, "₺")
                    for i, gider in enumerate(alt_kategori_giderler):
                        # Gider Türü sütununda görsel gruplama (sadece ilk satırda göster)
                        gider_turu_goster = ana_kategori if ana_kategori_ilk_satir else ""
                        
                        # Sıra No sütununda görsel gruplama (sadece ilk satırda genel sıra noyu göster)
                        sira_no_goster = genel_sira_no if ana_kategori_ilk_satir else ""
                        
                        # Tutar Toplamı sütununda görsel gruplama (sadece ilk satırda toplamı göster)
                        tutar_toplami_goster = f"{ana_kategori_toplam:.2f} {para_birimi}" if ana_kategori_ilk_satir else ""
                        
                        self.icmal_tree.insert("", "end", values=(
                            sira_no_goster,        # Sadece ilk satırda sıra numarası
                            gider_turu_goster,     # Sadece ilk satırda gider türü
                            alt_kategori,
                            f"{gider.tutar:.2f} {para_birimi}",  # Bireysel gider tutarı
                            gider.aciklama or "",
                            tutar_toplami_goster   # Sadece ilk satırda toplam
                        ), tags=(group_tag,))
                        
                        ana_kategori_ilk_satir = False
                        toplam_gider += gider.tutar
                
                # Bir sonraki gider türü için genel sıra numarasını artır
                if ana_kategori_toplam > 0:  # Sadece veri varsa artır
                    genel_sira_no += 1
            
            # Özet değerleri güncelle (sadece Giderler Toplamı)
            self.icmal_gider_toplam_label.configure(text=f"Gider Toplamı: {toplam_gider:.2f} ₺")
            
        except Exception as e:
            self.show_error(f"İcmal yüklenirken hata oluştu: {str(e)}")

    def setup_konut_mali_durumlari_tab(self) -> None:
        """Konut Mali Durumları tab'ı"""
        try:
            tab = self.tabview.tab("Konut Mali Durumları")

            # Ana container
            main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
            main_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # ===== ÜST KISIM: KAMU KURUMLARININ DURUMLARI =====
            kamu_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"], border_width=1, border_color=self.colors["primary"])
            kamu_frame.pack(fill="both", expand=True, padx=0, pady=(0, 6))

            # Başlık
            kamu_baslik = ctk.CTkLabel(
                kamu_frame,
                text="Kamu Kurumlarının Durumları",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=self.colors["primary"]
            )
            kamu_baslik.pack(anchor="w", padx=10, pady=(5, 3))

            # Tablo frame
            kamu_table_frame = ctk.CTkFrame(kamu_frame, fg_color=self.colors["surface"])
            kamu_table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

            self.konut_durum_tree = ttk.Treeview(
                kamu_table_frame,
                columns=("konut", "sayi", "m2", "aciklama"),
                show="headings",
                height=6
            )

            # Kolon başlıkları
            self.konut_durum_tree.heading("konut", text="Konut")
            self.konut_durum_tree.heading("sayi", text="Sayı")
            self.konut_durum_tree.heading("m2", text="m²")
            self.konut_durum_tree.heading("aciklama", text="Açıklama")

            # Kolon genişlikleri
            self.konut_durum_tree.column("konut", width=220, anchor="center")
            self.konut_durum_tree.column("sayi", width=100, anchor="center")
            self.konut_durum_tree.column("m2", width=120, anchor="center")
            self.konut_durum_tree.column("aciklama", width=300, anchor="center")

            # Scrollbar
            kamu_scrollbar = ttk.Scrollbar(kamu_table_frame, orient="vertical", command=self.konut_durum_tree.yview)
            self.konut_durum_tree.configure(yscrollcommand=kamu_scrollbar.set)

            self.konut_durum_tree.pack(side="left", fill="both", expand=True)
            kamu_scrollbar.pack(side="right", fill="y")

            # ===== ALT KISIM: MALİYET HESABI =====
            maliyet_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"], border_width=1, border_color=self.colors["primary"])
            maliyet_frame.pack(fill="both", expand=True, padx=0, pady=(0, 8))

            # Başlık
            maliyet_baslik = ctk.CTkLabel(
                maliyet_frame,
                text="Maliyet Hesabı",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=self.colors["primary"]
            )
            maliyet_baslik.pack(anchor="w", padx=10, pady=(5, 3))

            # Tablo frame
            maliyet_table_frame = ctk.CTkFrame(maliyet_frame, fg_color=self.colors["surface"])
            maliyet_table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

            self.maliyet_tree = ttk.Treeview(
                maliyet_table_frame,
                columns=("maliyet_turu", "tutar", "aciklama"),
                show="headings",
                height=8
            )

            # Kolon başlıkları
            self.maliyet_tree.heading("maliyet_turu", text="Maliyet Türü")
            self.maliyet_tree.heading("tutar", text="Tutar")
            self.maliyet_tree.heading("aciklama", text="Açıklama")

            # Kolon genişlikleri
            self.maliyet_tree.column("maliyet_turu", width=280, anchor="center")
            self.maliyet_tree.column("tutar", width=180, anchor="center")
            self.maliyet_tree.column("aciklama", width=400, anchor="center")

            # Scrollbar
            maliyet_scrollbar = ttk.Scrollbar(maliyet_table_frame, orient="vertical", command=self.maliyet_tree.yview)
            self.maliyet_tree.configure(yscrollcommand=maliyet_scrollbar.set)

            self.maliyet_tree.pack(side="left", fill="both", expand=True)
            maliyet_scrollbar.pack(side="right", fill="y")

            # ===== ALT KISIM: FİLTRELEME =====
            self.setup_konut_mali_filtreleme_paneli(main_frame)

            # Verileri yükle
            tab.after(100, self.load_konut_mali_durumlari)
        except Exception as e:
            print(f"Setup konut mali durumları hata: {str(e)}")
            self.show_error(f"Konut Mali Durumları sekmesi oluşturulurken hata oluştu: {str(e)}")

    def setup_konut_mali_filtreleme_paneli(self, parent: ctk.CTkFrame) -> None:
        """Konut Mali Durumları sekmesi için filtreleme paneli"""
    def setup_bilanco_filtreleme_paneli(self, parent: ctk.CTkFrame) -> None:
        """Bilanço sekmesi için filtreleme paneli"""
        filter_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors["background"],
            border_width=1,
            border_color=self.colors["primary"]
        )
        filter_frame.pack(fill="x", padx=0, pady=(0, 0))

        # Başlık
        filter_title = ctk.CTkLabel(
            filter_frame,
            text="Filtre",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["primary"]
        )
        filter_title.pack(anchor="w", padx=8, pady=(3, 3))

        # Filtre container
        filter_content = ctk.CTkFrame(filter_frame, fg_color=self.colors["background"])
        filter_content.pack(fill="x", padx=8, pady=(0, 5))

        # Filtre türü seçimi (Yıllık/Aylık)
        filtre_tur_label = ctk.CTkLabel(
            filter_content,
            text="Tür:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        filtre_tur_label.pack(side="left", padx=(0, 5))
        
        self.bilanco_filtre_tur_combo = ctk.CTkComboBox(
            filter_content,
            values=["Aylık", "Yıllık"],
            command=self.on_bilanco_filtre_tur_change,
            width=70,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.bilanco_filtre_tur_combo.set("Aylık")
        self.bilanco_filtre_tur_combo.pack(side="left", padx=(0, 15))

        # Yıl seçimi
        yil_label = ctk.CTkLabel(
            filter_content,
            text="Yıl:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        yil_label.pack(side="left", padx=(0, 5))

        # Veritabanından kullanılabilir yılları al
        yillar = self.get_veritabani_yillari()

        self.bilanco_yil_combo = ctk.CTkComboBox(
            filter_content,
            values=yillar,
            command=self.on_bilanco_filtre_change,
            width=65,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        
        # En yeni yılı seç
        if yillar:
            self.bilanco_yil_combo.set(yillar[-1])
        else:
            self.bilanco_yil_combo.set(str(datetime.now().year))
        
        self.bilanco_yil_combo.pack(side="left", padx=(0, 15))

        # Ay seçimi
        ay_label = ctk.CTkLabel(
            filter_content,
            text="Ay:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        ay_label.pack(side="left", padx=(0, 5))

        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.bilanco_ay_combo = ctk.CTkComboBox(
            filter_content,
            values=aylar,
            command=self.on_bilanco_filtre_change,
            width=75,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.bilanco_ay_combo.set(aylar[datetime.now().month - 1])
        self.bilanco_ay_combo.pack(side="left", padx=(0, 15))

        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filter_content,
            text="Temizle",
            command=self.temizle_bilanco_filtreleri,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=8, weight="bold"),
            height=24,
            width=60,
            corner_radius=3
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def setup_konut_mali_filtreleme_paneli(self, parent: ctk.CTkFrame) -> None:
        """Konut Mali Durumları sekmesi için filtreleme paneli"""
        filter_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors["background"],
            border_width=1,
            border_color=self.colors["primary"]
        )
        filter_frame.pack(fill="x", padx=0, pady=(0, 0))

        # Başlık
        filter_title = ctk.CTkLabel(
            filter_frame,
            text="Filtre",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["primary"]
        )
        filter_title.pack(anchor="w", padx=8, pady=(3, 3))

        # Filtre container
        filter_content = ctk.CTkFrame(filter_frame, fg_color=self.colors["background"])
        filter_content.pack(fill="x", padx=8, pady=(0, 5))

        # Filtre türü seçimi (Yıllık/Aylık)
        filtre_tur_label = ctk.CTkLabel(
            filter_content,
            text="Tür:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        filtre_tur_label.pack(side="left", padx=(0, 5))

        self.konut_mali_filtre_tur_combo = ctk.CTkComboBox(
            filter_content,
            values=["Aylık", "Yıllık"],
            command=self.on_konut_mali_filtre_tur_change,
            width=70,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.konut_mali_filtre_tur_combo.set("Aylık")
        self.konut_mali_filtre_tur_combo.pack(side="left", padx=(0, 15))

        # Yıl seçimi
        yil_label = ctk.CTkLabel(
            filter_content,
            text="Yıl:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        yil_label.pack(side="left", padx=(0, 5))

        # Veritabanından kullanılabilir yılları al
        yillar = self.get_veritabani_yillari()

        self.konut_mali_yil_combo = ctk.CTkComboBox(
            filter_content,
            values=yillar,
            command=self.on_konut_mali_filtre_change,
            width=65,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        
        # En yeni yılı seç
        if yillar:
            self.konut_mali_yil_combo.set(yillar[-1])
        else:
            self.konut_mali_yil_combo.set(str(datetime.now().year))
        
        self.konut_mali_yil_combo.pack(side="left", padx=(0, 15))

        # Ay seçimi
        ay_label = ctk.CTkLabel(
            filter_content,
            text="Ay:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        ay_label.pack(side="left", padx=(0, 5))

        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.konut_mali_ay_combo = ctk.CTkComboBox(
            filter_content,
            values=aylar,
            command=self.on_konut_mali_filtre_change,
            width=75,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.konut_mali_ay_combo.set(aylar[datetime.now().month - 1])
        self.konut_mali_ay_combo.pack(side="left", padx=(0, 15))

        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filter_content,
            text="Temizle",
            command=self.temizle_konut_mali_filtreleri,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=8, weight="bold"),
            height=24,
            width=60,
            corner_radius=3
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def on_konut_mali_filtre_tur_change(self, value: str) -> None:
        """Konut mali filtre türü değiştiğinde ay combo'yu göster/gizle"""
        if value == "Yıllık":
            self.konut_mali_ay_combo.configure(state="disabled")
        else:
            self.konut_mali_ay_combo.configure(state="normal")
        self.on_konut_mali_filtre_change(value)

    def on_konut_mali_filtre_change(self, value: str) -> None:
        """Konut mali filtreleme değiştiğinde verileri yenile"""
        self.load_konut_mali_durumlari()

    def temizle_konut_mali_filtreleri(self) -> None:
        """Konut mali filtre temizle"""
        from datetime import datetime
        self.konut_mali_filtre_tur_combo.set("Aylık")
        self.konut_mali_yil_combo.set(str(datetime.now().year))
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.konut_mali_ay_combo.set(aylar[datetime.now().month - 1])
        self.konut_mali_ay_combo.configure(state="normal")
        self.load_konut_mali_durumlari()

    def setup_bos_konut_listesi_tab(self) -> None:
        """Boş Konut Maliyet Analizi tab'ı"""
        tab = self.tabview.tab("Boş Konut Listesi")

        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # ===== ÜST KISIM: BAŞLIK =====
        title_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        title_frame.pack(fill="x", padx=0, pady=(0, 8))

        title_label = ctk.CTkLabel(
            title_frame,
            text="Boş Konut Maliyet Analizi",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(anchor="w", padx=10, pady=(5, 5))

        # ===== ORTADA: TABLO =====
        table_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"])
        table_frame.pack(fill="both", expand=True, padx=0, pady=(0, 8))

        # Boş konut listesi tablosu
        self.bos_konut_tree = ttk.Treeview(
            table_frame,
            columns=("sira_no", "daire_adi", "daire_no", "alan_m2", "ilk_tarih", "son_tarih", "sorumlu_gun_sayisi", "konut_aidat_bedeli"),
            show="headings",
            height=15
        )

        # Kolon başlıkları
        self.bos_konut_tree.heading("sira_no", text="Sıra No")
        self.bos_konut_tree.heading("daire_adi", text="Daire Adı")
        self.bos_konut_tree.heading("daire_no", text="Daire No")
        self.bos_konut_tree.heading("alan_m2", text="Alan(m2)")
        self.bos_konut_tree.heading("ilk_tarih", text="İlk Tarih")
        self.bos_konut_tree.heading("son_tarih", text="Son Tarih")
        self.bos_konut_tree.heading("sorumlu_gun_sayisi", text="Sorumlu Gün Sayısı")
        self.bos_konut_tree.heading("konut_aidat_bedeli", text="Konut Aidat Bedeli")

        # Kolon genişlikleri
        self.bos_konut_tree.column("sira_no", width=60, anchor="center")
        self.bos_konut_tree.column("daire_adi", width=120, anchor="center")
        self.bos_konut_tree.column("daire_no", width=70, anchor="center")
        self.bos_konut_tree.column("alan_m2", width=80, anchor="center")
        self.bos_konut_tree.column("ilk_tarih", width=100, anchor="center")
        self.bos_konut_tree.column("son_tarih", width=100, anchor="center")
        self.bos_konut_tree.column("sorumlu_gun_sayisi", width=120, anchor="center")
        self.bos_konut_tree.column("konut_aidat_bedeli", width=120, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.bos_konut_tree.yview)
        self.bos_konut_tree.configure(yscrollcommand=scrollbar.set)

        self.bos_konut_tree.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        scrollbar.pack(side="right", fill="y", pady=0)

        # ===== ALT KISIM: FİLTRELEME =====
        self.setup_bos_konut_filtreleme_paneli(main_frame)

        # Verileri yükle
        tab.after(100, self.load_bos_konut_listesi)

    def get_veritabani_yillari(self) -> List[str]:
        """Veritabanında bulunan tüm işlem yıllarını al"""
        try:
            yillar_set = set()
            
            # Gelirlerden yılları al
            gelirler = self.finans_controller.get_gelirler()
            for gelir in gelirler:
                if gelir.tarih:
                    yillar_set.add(gelir.tarih.year)
            
            # Giderlerden yılları al
            giderler = self.finans_controller.get_giderler()
            for gider in giderler:
                if gider.tarih:
                    yillar_set.add(gider.tarih.year)
            
            # Transferlerden yılları al
            transferler = self.finans_controller.get_transferler()
            for transfer in transferler:
                if transfer.tarih:
                    yillar_set.add(transfer.tarih.year)
            
            # Eğer hiç yıl bulunamadıysa, cari yılı ekle
            if not yillar_set:
                from datetime import datetime
                yillar_set.add(datetime.now().year)
            
            # Sıralı şekilde döndür (eski → yeni)
            yillar_liste = sorted([str(y) for y in yillar_set])
            return yillar_liste
        except Exception as e:
            # Hata durumunda cari yılı döndür
            from datetime import datetime
            return [str(datetime.now().year)]

    def setup_tum_islem_filtreleme_paneli(self, parent: ctk.CTkFrame) -> None:
        """Tüm İşlem Detayları için filtreleme paneli"""
        filter_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors["background"],
            border_width=1,
            border_color=self.colors["primary"]
        )
        filter_frame.pack(fill="x", padx=0, pady=(0, 0))

        # Başlık
        filter_title = ctk.CTkLabel(
            filter_frame,
            text="Filtre",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["primary"]
        )
        filter_title.pack(anchor="w", padx=8, pady=(3, 3))

        # Filtre container
        filter_content = ctk.CTkFrame(filter_frame, fg_color=self.colors["background"])
        filter_content.pack(fill="x", padx=8, pady=(0, 5))

        # Filtre türü seçimi (Yıllık/Aylık)
        filtre_tur_label = ctk.CTkLabel(
            filter_content,
            text="Tür:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        filtre_tur_label.pack(side="left", padx=(0, 5))

        from datetime import datetime
        
        self.islem_filtre_tur_combo = ctk.CTkComboBox(
            filter_content,
            values=["Aylık", "Yıllık"],
            command=self.on_islem_filtre_tur_change,
            width=70,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.islem_filtre_tur_combo.set("Aylık")
        self.islem_filtre_tur_combo.pack(side="left", padx=(0, 15))

        # Yıl seçimi - Veritabanındaki yıllardan dinamik olarak oluştur
        yil_label = ctk.CTkLabel(
            filter_content,
            text="Yıl:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        yil_label.pack(side="left", padx=(0, 5))

        # Veritabanından kullanılabilir yılları al
        yillar = self.get_veritabani_yillari()

        self.islem_yil_combo = ctk.CTkComboBox(
            filter_content,
            values=yillar,
            command=self.on_islem_filtre_change,
            width=65,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        
        # En yeni yılı seç
        if yillar:
            self.islem_yil_combo.set(yillar[-1])  # Son yıl (en yeni)
        else:
            self.islem_yil_combo.set(str(datetime.now().year))
        
        self.islem_yil_combo.pack(side="left", padx=(0, 15))

        # Ay seçimi (başlangıçta görünür)
        ay_label = ctk.CTkLabel(
            filter_content,
            text="Ay:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        ay_label.pack(side="left", padx=(0, 5))

        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.islem_ay_combo = ctk.CTkComboBox(
            filter_content,
            values=aylar,
            command=self.on_islem_filtre_change,
            width=75,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.islem_ay_combo.set(aylar[datetime.now().month - 1])
        self.islem_ay_combo.pack(side="left", padx=(0, 15))

        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filter_content,
            text="Temizle",
            command=self.temizle_islem_filtreleri,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=8, weight="bold"),
            height=24,
            width=60,
            corner_radius=3
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def on_islem_filtre_tur_change(self, value: str) -> None:
        """Filtre türü değiştiğinde ay combo'yu göster/gizle"""
        if value == "Yıllık":
            self.islem_ay_combo.configure(state="disabled")
        else:
            self.islem_ay_combo.configure(state="normal")
        self.on_islem_filtre_change(value)

    def on_islem_filtre_change(self, value: str) -> None:
        """Filtreleme değiştiğinde verileri yenile"""
        # Yıl combo box'undaki yılları güncelle (yeni veri giriş durumunda)
        self.guncelle_islem_yil_combo()
        self.load_tum_islem_detaylari()
    
    def guncelle_islem_yil_combo(self) -> None:
        """Yıl combo box'unu veritabanındaki güncel yıllarla güncelle"""
        try:
            if hasattr(self, 'islem_yil_combo') and self.islem_yil_combo is not None:
                yillar = self.get_veritabani_yillari()
                self.islem_yil_combo.configure(values=yillar)
                
                # Seçili yıl hala listede varsa tut, yoksa en yeni yılı seç
                current_value = self.islem_yil_combo.get()
                if current_value not in yillar and yillar:
                    self.islem_yil_combo.set(yillar[-1])  # En yeni yıl
        except Exception as e:
            # Sessizce fail (hata durumunda combo box olduğu gibi kalır)
            pass

    def on_icmal_filtre_tur_change(self, value: str) -> None:
        """İcmal filtre türü değiştiğinde ay combo'yu göster/gizle"""
        if value == "Yıllık":
            self.icmal_ay_combo.configure(state="disabled")
        else:
            self.icmal_ay_combo.configure(state="normal")
        self.on_icmal_filtre_change(value)
        
    def on_icmal_filtre_change(self, value: str) -> None:
        """İcmal filtreleme değiştiğinde verileri yenile"""
        # Yıl combo box'undaki yılları güncelle (yeni veri giriş durumunda)
        self.guncelle_icmal_yil_combo()
        self.load_icmal()
        
    def guncelle_icmal_yil_combo(self) -> None:
        """İcmal yıl combo box'unu veritabanındaki güncel yıllarla güncelle"""
        try:
            if hasattr(self, 'icmal_yil_combo') and self.icmal_yil_combo is not None:
                yillar = self.get_veritabani_yillari()
                self.icmal_yil_combo.configure(values=yillar)
                
                # Seçili yıl hala listede varsa tut, yoksa en yeni yılı seç
                current_value = self.icmal_yil_combo.get()
                if current_value not in yillar and yillar:
                    self.icmal_yil_combo.set(yillar[-1])  # En yeni yıl
        except Exception as e:
            # Sessizce fail (hata durumunda combo box olduğu gibi kalır)
            pass


    def temizle_islem_filtreleri(self) -> None:
        """İşlem filtreleri temizle"""
        from datetime import datetime
        self.islem_filtre_tur_combo.set("Aylık")
        self.islem_yil_combo.set(str(datetime.now().year))
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.islem_ay_combo.set(aylar[datetime.now().month - 1])
        self.islem_ay_combo.configure(state="normal")
        self.load_tum_islem_detaylari()

    # Veri yükleme metodları
    def load_tum_islem_detaylari(self) -> None:
        """Tüm işlem detaylarını yükle ve filtreleme uygula"""
        try:
            # Treeview'i temizle
            for item in self.islem_tree.get_children():
                self.islem_tree.delete(item)

            # Filtre parametrelerini al (combo box'lar varsa)
            from datetime import datetime
            
            # Combo box'ların varlığını kontrol et
            if not hasattr(self, 'islem_filtre_tur_combo') or self.islem_filtre_tur_combo is None:
                # İlk çağrıda combo box'lar henüz oluşturulmamış, varsayılan değerleri kullan
                filtre_tur = "Aylık"
                yil = datetime.now().year
                ay = datetime.now().month
            else:
                filtre_tur = self.islem_filtre_tur_combo.get()  # "Aylık" veya "Yıllık"
                yil = int(self.islem_yil_combo.get())
                
                # Ayı sayıya çevir (Ocak=1, Şubat=2, ...)
                aylar_dict = {
                    "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4,
                    "Mayıs": 5, "Haziran": 6, "Temmuz": 7, "Ağustos": 8,
                    "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12
                }
                ay_text = self.islem_ay_combo.get()
                ay = aylar_dict.get(ay_text, datetime.now().month)

            # Tüm işlemleri al
            gelirler = self.finans_controller.get_gelirler()
            giderler = self.finans_controller.get_giderler()
            transferler = self.finans_controller.get_transferler()

            # Özet değişkenleri
            donem_toplam_gelir = 0.0
            donem_toplam_gider = 0.0

            # Gelirleri filtreleme ve ekleme
            for gelir in gelirler:
                if self.uygula_tarih_filtresi(gelir.tarih, filtre_tur, yil, ay):
                    donem_toplam_gelir += gelir.tutar
                    ana_kat = gelir.kategori.ana_kategori.name if (gelir.kategori and gelir.kategori.ana_kategori) else ""
                    alt_kat = gelir.kategori.name if gelir.kategori else ""
                    # Para birimi ile tutar göster
                    para_birimi = gelir.hesap.para_birimi if gelir.hesap and hasattr(gelir.hesap, 'para_birimi') else "₺"
                    tutar_gosterimi = f"{gelir.tutar:.2f} {para_birimi}"
                    self.islem_tree.insert("", "end", values=(
                        f"İşlem#{gelir.id}",
                        gelir.tarih.strftime("%d.%m.%Y") if gelir.tarih else "",
                        gelir.aciklama or "",
                        ana_kat,
                        alt_kat,
                        gelir.hesap.ad if gelir.hesap else "",
                        tutar_gosterimi,
                        "Gelir"
                    ), tags=("gelir",))

            # Giderleri filtreleme ve ekleme
            for gider in giderler:
                if self.uygula_tarih_filtresi(gider.tarih, filtre_tur, yil, ay):
                    donem_toplam_gider += gider.tutar
                    ana_kat = gider.kategori.ana_kategori.name if (gider.kategori and gider.kategori.ana_kategori) else ""
                    alt_kat = gider.kategori.name if gider.kategori else ""
                    # Para birimi ile tutar göster
                    para_birimi = gider.hesap.para_birimi if gider.hesap and hasattr(gider.hesap, 'para_birimi') else "₺"
                    tutar_gosterimi = f"{gider.tutar:.2f} {para_birimi}"
                    self.islem_tree.insert("", "end", values=(
                        f"İşlem#{gider.id}",
                        gider.tarih.strftime("%d.%m.%Y") if gider.tarih else "",
                        gider.aciklama or "",
                        ana_kat,
                        alt_kat,
                        gider.hesap.ad if gider.hesap else "",
                        tutar_gosterimi,
                        "Gider"
                    ), tags=("gider",))

            # Transferleri filtreleme ve ekleme
            for transfer in transferler:
                if self.uygula_tarih_filtresi(transfer.tarih, filtre_tur, yil, ay):
                    # Para birimi ile tutar göster
                    para_birimi = transfer.hesap.para_birimi if transfer.hesap and hasattr(transfer.hesap, 'para_birimi') else "₺"
                    tutar_gosterimi = f"{transfer.tutar:.2f} {para_birimi}"
                    self.islem_tree.insert("", "end", values=(
                        f"İşlem#{transfer.id}",
                        transfer.tarih.strftime("%d.%m.%Y") if transfer.tarih else "",
                        transfer.aciklama or "",
                        "",
                        "",
                        f"{transfer.hesap.ad if transfer.hesap else ''} → {transfer.hedef_hesap.ad if transfer.hedef_hesap else ''}",
                        tutar_gosterimi,
                        "Transfer"
                    ), tags=("transfer",))

            # Renk kodlaması
            self.islem_tree.tag_configure("gelir", background="#e8f5e8")
            self.islem_tree.tag_configure("gider", background="#ffeaea")
            self.islem_tree.tag_configure("transfer", background="#e8f0ff")

            # Özet bilgilerini güncelle
            donem_net_bakiye = donem_toplam_gelir - donem_toplam_gider
            self.donem_toplam_gelir_label.configure(text=f"{donem_toplam_gelir:.2f} ₺")
            self.donem_toplam_gider_label.configure(text=f"{donem_toplam_gider:.2f} ₺")
            self.donem_net_bakiye_label.configure(text=f"{donem_net_bakiye:.2f} ₺")

            # Net bakiyeye göre renk ayarla
            if donem_net_bakiye >= 0:
                self.donem_net_bakiye_label.configure(text_color=self.colors["success"])
            else:
                self.donem_net_bakiye_label.configure(text_color=self.colors["error"])

        except Exception as e:
            self.show_error(f"İşlem detayları yüklenirken hata oluştu: {str(e)}")

    def uygula_tarih_filtresi(self, islem_tarihi: datetime, filtre_tur: str, yil: int, ay: int) -> bool:
        """Tarih filtresini uygula"""
        if not islem_tarihi:
            return False
        
        islem_yil = islem_tarihi.year
        islem_ay = islem_tarihi.month
        
        if filtre_tur == "Yıllık":
            return islem_yil == yil
        else:  # Aylık
            return islem_yil == yil and islem_ay == ay

    def setup_bilanco_filtreleme_paneli(self, parent: ctk.CTkFrame) -> None:
        """Bilanço sekmesi için filtreleme paneli"""
        filter_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors["background"],
            border_width=1,
            border_color=self.colors["primary"]
        )
        filter_frame.pack(fill="x", padx=0, pady=(0, 0))

        # Başlık
        filter_title = ctk.CTkLabel(
            filter_frame,
            text="Filtre",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["primary"]
        )
        filter_title.pack(anchor="w", padx=8, pady=(3, 3))

        # Filtre container
        filter_content = ctk.CTkFrame(filter_frame, fg_color=self.colors["background"])
        filter_content.pack(fill="x", padx=8, pady=(0, 5))

        # Filtre türü seçimi (Yıllık/Aylık)
        filtre_tur_label = ctk.CTkLabel(
            filter_content,
            text="Tür:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        filtre_tur_label.pack(side="left", padx=(0, 5))

        from datetime import datetime
        
        self.bilanco_filtre_tur_combo = ctk.CTkComboBox(
            filter_content,
            values=["Aylık", "Yıllık"],
            command=self.on_bilanco_filtre_tur_change,
            width=70,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.bilanco_filtre_tur_combo.set("Aylık")
        self.bilanco_filtre_tur_combo.pack(side="left", padx=(0, 15))

        # Yıl seçimi
        yil_label = ctk.CTkLabel(
            filter_content,
            text="Yıl:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        yil_label.pack(side="left", padx=(0, 5))

        # Veritabanından kullanılabilir yılları al
        yillar = self.get_veritabani_yillari()

        self.bilanco_yil_combo = ctk.CTkComboBox(
            filter_content,
            values=yillar,
            command=self.on_bilanco_filtre_change,
            width=65,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        
        # En yeni yılı seç
        if yillar:
            self.bilanco_yil_combo.set(yillar[-1])
        else:
            self.bilanco_yil_combo.set(str(datetime.now().year))
        
        self.bilanco_yil_combo.pack(side="left", padx=(0, 15))

        # Ay seçimi
        ay_label = ctk.CTkLabel(
            filter_content,
            text="Ay:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        ay_label.pack(side="left", padx=(0, 5))

        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.bilanco_ay_combo = ctk.CTkComboBox(
            filter_content,
            values=aylar,
            command=self.on_bilanco_filtre_change,
            width=75,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.bilanco_ay_combo.set(aylar[datetime.now().month - 1])
        self.bilanco_ay_combo.pack(side="left", padx=(0, 15))

        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filter_content,
            text="Temizle",
            command=self.temizle_bilanco_filtreleri,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=8, weight="bold"),
            height=24,
            width=60,
            corner_radius=3
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def on_bilanco_filtre_tur_change(self, value: str) -> None:
        """Bilanço filtre türü değiştiğinde ay combo'yu göster/gizle"""
        if value == "Yıllık":
            self.bilanco_ay_combo.configure(state="disabled")
        else:
            self.bilanco_ay_combo.configure(state="normal")
        self.on_bilanco_filtre_change(value)

    def on_bilanco_filtre_change(self, value: str) -> None:
        """Bilanço filtreleme değiştiğinde verileri yenile"""
        self.load_bilanco()

    def temizle_bilanco_filtreleri(self) -> None:
        """Bilanço filtreleri temizle"""
        self.bilanco_filtre_tur_combo.set("Aylık")
        self.bilanco_yil_combo.set(str(datetime.now().year))
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.bilanco_ay_combo.set(aylar[datetime.now().month - 1])
        self.bilanco_ay_combo.configure(state="normal")
        self.load_bilanco()

    def load_bilanco(self) -> None:
        """Bilanço verilerini yükle"""
        try:
            # Treeview'leri temizle
            for item in self.bilanco_tree.get_children():
                self.bilanco_tree.delete(item)

            # Filtre parametrelerini al
            if not hasattr(self, 'bilanco_filtre_tur_combo') or self.bilanco_filtre_tur_combo is None:
                filtre_tur = "Aylık"
                yil = datetime.now().year
                ay = datetime.now().month
            else:
                filtre_tur = self.bilanco_filtre_tur_combo.get()
                yil = int(self.bilanco_yil_combo.get())
                
                aylar_dict = {
                    "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4,
                    "Mayıs": 5, "Haziran": 6, "Temmuz": 7, "Ağustos": 8,
                    "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12
                }
                ay_text = self.bilanco_ay_combo.get()
                ay = aylar_dict.get(ay_text, datetime.now().month)

            # Tüm işlemleri al
            gelirler = self.finans_controller.get_gelirler()
            giderler = self.finans_controller.get_giderler()

            # Seçilen dönem başlangıcını belirle
            if filtre_tur == "Aylık":
                donem_baslangic = datetime(yil, ay, 1)
                # Ay sonunu belirle
                if ay == 12:
                    donem_son = datetime(yil + 1, 1, 1)
                else:
                    donem_son = datetime(yil, ay + 1, 1)
            else:  # Yıllık
                donem_baslangic = datetime(yil, 1, 1)
                donem_son = datetime(yil + 1, 1, 1)

            # Dönem öncesi net bakiye hesapla (seçilen dönemden önceki tüm işlemlerin toplamı)
            onceki_gelir_toplam = sum(g.tutar for g in gelirler if g.tarih < donem_baslangic)
            onceki_gider_toplam = sum(g.tutar for g in giderler if g.tarih < donem_baslangic)
            onceki_donem_bakiye = onceki_gelir_toplam - onceki_gider_toplam

            # Dönem içi gelir ve giderleri hesapla
            donem_toplam_gelir: float = 0.0
            donem_toplam_gider: float = 0.0
            gelir_kategorileri: dict = {}  # {ana_kategori: toplam}
            gider_kategorileri: dict = {}  # {ana_kategori: toplam}
            
            # Gelirleri işle
            gelir_kategorileri_para: dict = {}  # {ana_kategori: {tutar: toplam, para_birimi: ₺}}
            for gelir in gelirler:
                if self.uygula_tarih_filtresi(gelir.tarih, filtre_tur, yil, ay):
                    donem_toplam_gelir += float(gelir.tutar)
                    
                    # Kategori bilgisini al
                    ana_kat = gelir.kategori.ana_kategori.name if (gelir.kategori and gelir.kategori.ana_kategori) else "Tanımsız"
                    
                    # Para birimini al
                    para_birimi = "₺"
                    if gelir.hesap:
                        para_birimi = gelir.hesap.para_birimi or "₺"
                    
                    if ana_kat not in gelir_kategorileri_para:
                        gelir_kategorileri_para[ana_kat] = {"tutar": 0.0, "para_birimi": str(para_birimi)}
                    gelir_kategorileri_para[ana_kat]["tutar"] += float(gelir.tutar)
                    gelir_kategorileri[ana_kat] = float(gelir_kategorileri_para[ana_kat]["tutar"])
            
            # Giderleri işle
            gider_kategorileri_para: dict = {}  # {ana_kategori: {tutar: toplam, para_birimi: ₺}}
            for gider in giderler:
                if self.uygula_tarih_filtresi(gider.tarih, filtre_tur, yil, ay):
                    donem_toplam_gider += float(gider.tutar)
                    
                    # Kategori bilgisini al
                    ana_kat = gider.kategori.ana_kategori.name if (gider.kategori and gider.kategori.ana_kategori) else "Tanımsız"
                    
                    # Para birimini al
                    para_birimi = "₺"
                    if gider.hesap:
                        para_birimi = gider.hesap.para_birimi or "₺"
                    
                    if ana_kat not in gider_kategorileri_para:
                        gider_kategorileri_para[ana_kat] = {"tutar": 0.0, "para_birimi": str(para_birimi)}
                    gider_kategorileri_para[ana_kat]["tutar"] += float(gider.tutar)
                    gider_kategorileri[ana_kat] = float(gider_kategorileri_para[ana_kat]["tutar"])
            
            # Dönem sonu bakiyesi = Önceki dönem bakiyesi + (dönem gelir - dönem gider)
            donem_sonu_bakiye = float(onceki_donem_bakiye) + (float(donem_toplam_gelir) - float(donem_toplam_gider))
            
            # Detayları tabloya ekle (önce gelirler, sonra giderler)
            for ana_kat in sorted(gelir_kategorileri.keys()):
                gelir_para_birimi: str = str(gelir_kategorileri_para[ana_kat]["para_birimi"])
                self.bilanco_tree.insert("", "end", values=(
                    "Gelir",
                    ana_kat,
                    f"{float(gelir_kategorileri[ana_kat]):.2f} {gelir_para_birimi}"
                ), tags=("gelir",))
            
            for ana_kat in sorted(gider_kategorileri.keys()):
                gider_para_birimi: str = str(gider_kategorileri_para[ana_kat]["para_birimi"])
                self.bilanco_tree.insert("", "end", values=(
                    "Gider",
                    ana_kat,
                    f"{float(gider_kategorileri[ana_kat]):.2f} {gider_para_birimi}"
                ), tags=("gider",))

            # Özet değerlerini güncelle
            self.bilanco_onceki_bakiye_label.configure(
                text=f"{onceki_donem_bakiye:.2f} ₺"
            )
            self.bilanco_donem_gelir_label.configure(
                text=f"{donem_toplam_gelir:.2f} ₺"
            )
            self.bilanco_donem_gider_label.configure(
                text=f"{donem_toplam_gider:.2f} ₺"
            )
            self.bilanco_son_bakiye_label.configure(
                text=f"{donem_sonu_bakiye:.2f} ₺"
            )

        except Exception as e:
            self.show_error(f"Bilanço yüklenirken hata oluştu: {str(e)}")

    def load_konut_mali_durumlari(self) -> None:
        """Konut mali durumlarını yükle"""
        try:
            # Treeview'leri temizle
            for item in self.konut_durum_tree.get_children():
                self.konut_durum_tree.delete(item)
            for item in self.maliyet_tree.get_children():
                self.maliyet_tree.delete(item)

            # Filtre parametrelerini al
            from datetime import datetime
            
            if not hasattr(self, 'konut_mali_filtre_tur_combo') or self.konut_mali_filtre_tur_combo is None:
                filtre_tur = "Aylık"
                yil = datetime.now().year
                ay = datetime.now().month
            else:
                filtre_tur = self.konut_mali_filtre_tur_combo.get()
                yil = int(self.konut_mali_yil_combo.get())
                
                aylar_dict = {
                    "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4,
                    "Mayıs": 5, "Haziran": 6, "Temmuz": 7, "Ağustos": 8,
                    "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12
                }
                ay_text = self.konut_mali_ay_combo.get()
                ay = aylar_dict.get(ay_text, datetime.now().month)

            # Seçilen dönem başlangıcını ve sonunu belirle
            if filtre_tur == "Aylık":
                donem_baslangic = datetime(yil, ay, 1)
                # Ay sonunu belirle
                if ay == 12:
                    donem_son = datetime(yil + 1, 1, 1)
                else:
                    donem_son = datetime(yil, ay + 1, 1)
            else:  # Yıllık
                donem_baslangic = datetime(yil, 1, 1)
                donem_son = datetime(yil + 1, 1, 1)

            # Daireleri yükle (eager loading ile)
            db = get_db()
            daireler = db.query(Daire).options(
                joinedload(Daire.sakini),
                joinedload(Daire.blok)
            ).filter(Daire.aktif == True).all()
            db.close()
            
            # Dairenin seçili dönemde dolu olup olmadığını belirle
            def daire_dolu_mu(daire: Daire, donem_baslangic: datetime, donem_son: datetime) -> bool:
                """Dairenin belirtilen dönemde dolu olup olmadığını kontrol et"""
                if not daire.sakini:
                    return False
                
                sakin = daire.sakini
                # Tahsis tarihi veya giriş tarihi
                tahsis = sakin.tahsis_tarihi if sakin.tahsis_tarihi else sakin.giris_tarihi
                cikis = sakin.cikis_tarihi
                
                if not tahsis:
                    return False
                
                # Tahsis tarihi dönem sonundan sonra mı?
                if tahsis >= donem_son:
                    return False
                
                # Çıkış tarihi dönem başlangıcından önce mi?
                if cikis and cikis <= donem_baslangic:
                    return False
                
                return True
            
            # İstatistikleri hesapla
            toplam_konut_sayisi = len(daireler)
            dolu_konut_sayisi = sum(1 for daire in daireler if daire_dolu_mu(daire, donem_baslangic, donem_son))
            bos_konut_sayisi = toplam_konut_sayisi - dolu_konut_sayisi
            
            # m² hesaplamaları
            toplam_m2 = sum(daire.kiraya_esas_alan or 0 for daire in daireler)
            dolu_m2 = sum(daire.kiraya_esas_alan or 0 for daire in daireler if daire_dolu_mu(daire, donem_baslangic, donem_son))
            bos_m2 = toplam_m2 - dolu_m2
            
            # Üst tablo: Kamu Kurumlarının Durumları
            self.konut_durum_tree.insert("", "end", values=(
                "Toplam Konut sayısı",
                toplam_konut_sayisi,
                f"{toplam_m2:.2f}",
                "Sistemde kayıtlı toplam konut sayısı"
            ))
            
            self.konut_durum_tree.insert("", "end", values=(
                "Dolu Konut Sayısı",
                dolu_konut_sayisi,
                f"{dolu_m2:.2f}",
                "Aktif olarak kullanılan konutlar"
            ))
            
            self.konut_durum_tree.insert("", "end", values=(
                "Boş Konut Sayısı",
                bos_konut_sayisi,
                f"{bos_m2:.2f}",
                "Kullanılmayan/boş konutlar"
            ))
            
            # Maliyet hesaplamaları (filtrelenmiş giderler)
            # Giderler toplamı - filtreli
            giderler = self.finans_controller.get_giderler()
            filtered_giderler = [gider for gider in giderler if self.uygula_tarih_filtresi(gider.tarih, filtre_tur, yil, ay)]
            toplam_gider = sum(gider.tutar for gider in filtered_giderler)
            
            # Konut başına düşen maliyet
            konut_basina_maliyet = toplam_gider / toplam_konut_sayisi if toplam_konut_sayisi > 0 else 0
            
            # Boş konutların toplam maliyeti
            bos_konutlarin_maliyet = bos_konut_sayisi * konut_basina_maliyet
            
            # Alt tablo: Maliyet Hesabı
            self.maliyet_tree.insert("", "end", values=(
                "Giderler Toplamı",
                f"{toplam_gider:.2f} ₺",
                "Tüm gider kayıtlarının toplamı"
            ))
            
            self.maliyet_tree.insert("", "end", values=(
                "Konut Başına Düşen Maliyet",
                f"{konut_basina_maliyet:.2f} ₺",
                "Toplam gider / toplam konut sayısı"
            ))
            
            self.maliyet_tree.insert("", "end", values=(
                "Boş Konutların Toplam Maliyeti",
                f"{bos_konutlarin_maliyet:.2f} ₺",
                "Boş konut sayısı × konut başına düşen maliyet"
            ))
            
        except Exception as e:
            self.show_error(f"Konut mali durumları yüklenirken hata oluştu: {str(e)}")

    def setup_bos_konut_filtreleme_paneli(self, parent: ctk.CTkFrame) -> None:
        """Boş konut listesi için filtreleme paneli"""
        filter_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors["background"],
            border_width=1,
            border_color=self.colors["primary"]
        )
        filter_frame.pack(fill="x", padx=0, pady=(0, 0))

        # Başlık
        filter_title = ctk.CTkLabel(
            filter_frame,
            text="Filtre",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["primary"]
        )
        filter_title.pack(anchor="w", padx=8, pady=(3, 3))

        # Filtre container
        filter_content = ctk.CTkFrame(filter_frame, fg_color=self.colors["background"])
        filter_content.pack(fill="x", padx=8, pady=(0, 5))

        from datetime import datetime

        # Yıl seçimi
        yil_label = ctk.CTkLabel(
            filter_content,
            text="Yıl:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        yil_label.pack(side="left", padx=(0, 5))

        # Veritabanından kullanılabilir yılları al
        yillar = self.get_veritabani_yillari()

        self.bos_konut_yil_combo = ctk.CTkComboBox(
            filter_content,
            values=yillar,
            command=self.on_bos_konut_yil_change,
            width=65,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )

        # En yeni yılı seç
        if yillar:
            self.bos_konut_yil_combo.set(yillar[-1])
        else:
            self.bos_konut_yil_combo.set(str(datetime.now().year))

        self.bos_konut_yil_combo.pack(side="left", padx=(0, 15))

        # Ay seçimi
        ay_label = ctk.CTkLabel(
            filter_content,
            text="Ay:",
            font=ctk.CTkFont(size=8),
            text_color=self.colors["text"]
        )
        ay_label.pack(side="left", padx=(0, 5))

        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                 "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.bos_konut_ay_combo = ctk.CTkComboBox(
            filter_content,
            values=aylar,
            command=self.on_bos_konut_filtre_change,
            width=75,
            height=24,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=8)
        )
        self.bos_konut_ay_combo.set(aylar[datetime.now().month - 1])
        self.bos_konut_ay_combo.pack(side="left", padx=(0, 15))

        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filter_content,
            text="Temizle",
            command=self.temizle_bos_konut_filtreleri,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=8, weight="bold"),
            height=24,
            width=60,
            corner_radius=3
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def on_bos_konut_yil_change(self, value: str) -> None:
        """Yıl değiştiğinde verileri yenile"""
        self.load_bos_konut_listesi()

    def on_bos_konut_filtre_change(self, value: str) -> None:
        """Boş konut filtresi değiştiğinde verileri yenile"""
        self.load_bos_konut_listesi()

    def temizle_bos_konut_filtreleri(self) -> None:
        """Boş konut filtreleri temizle"""
        from datetime import datetime
        yillar = self.get_veritabani_yillari()
        if yillar:
            self.bos_konut_yil_combo.set(yillar[-1])
        else:
            self.bos_konut_yil_combo.set(str(datetime.now().year))
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                 "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.bos_konut_ay_combo.set(aylar[datetime.now().month - 1])
        self.load_bos_konut_listesi()

    def load_bos_konut_listesi(self) -> None:
        """Boş konut listesini yükle ve hesaplamaları yap"""
        try:
            # Treeview'i temizle
            for item in self.bos_konut_tree.get_children():
                self.bos_konut_tree.delete(item)

            # Veritabanından verileri al
            db = get_db()
            
            # Daireler (eager loading ile)
            daireler = db.query(Daire).options(
                joinedload(Daire.sakini),
                joinedload(Daire.blok).joinedload(Blok.lojman)
            ).filter(Daire.aktif == True).all()
            
            # Bloklar
            bloklar = db.query(Blok).all()
            
            # Lojmanlar
            lojmanlar = db.query(Lojman).all()
            
            # Sakinler (hem aktif hem pasif - boş konut analizi için gerekli)
            sakinler = db.query(Sakin).all()  # Tüm sakinleri al (aktif ve pasif)
            
            # Giderler (FinansIslem - tip='Gider')
            giderler = db.query(FinansIslem).filter(FinansIslem.tur == 'Gider').all()
            
            db.close()
            
            # Filtre değerlerini al
            from datetime import datetime
            
            if not hasattr(self, 'bos_konut_yil_combo') or self.bos_konut_yil_combo is None:
                yil = datetime.now().year
                ay = datetime.now().month
            else:
                yil = int(self.bos_konut_yil_combo.get())
                
                aylar_dict = {
                    "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4,
                    "Mayıs": 5, "Haziran": 6, "Temmuz": 7, "Ağustos": 8,
                    "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12
                }
                ay_text = self.bos_konut_ay_combo.get()
                ay = aylar_dict.get(ay_text, datetime.now().month)
            
            # Verileri hesaplama fonksiyonu için format et
            daire_listesi = [
                {
                    'id': d.id,
                    'daire_no': d.daire_no,
                    'bagliBlokId': d.blok_id,
                    'kiraya_esasi_alan': d.kiraya_esas_alan
                }
                for d in daireler
            ]
            
            blok_listesi = [
                {
                    'id': b.id,
                    'blok_adi': b.ad,
                    'bagliLojmanId': b.lojman_id
                }
                for b in bloklar
            ]
            
            lojman_listesi = [
                {
                    'id': l.id,
                    'lojman_adi': l.ad
                }
                for l in lojmanlar
            ]
            
            gider_kayitlari = [
                {
                    'id': g.id,
                    'tutar': g.tutar_kurus / 100.0,  # kuruş → TL
                    'islem_tarihi': g.tarih
                }
                for g in giderler
            ]
            
            sakin_listesi = [
                {
                    'daire_id': s.daire_id or s.eski_daire_id,  # Aktif daire veya eski daire
                    'tahsis_tarihi': s.tahsis_tarihi,
                    'giris_tarihi': s.giris_tarihi,
                    'cikis_tarihi': s.cikis_tarihi  # Çıkış tarihi (pasif sakinler için)
                }
                for s in sakinler
                if (s.daire_id or s.eski_daire_id)  # Hiç daire kaydı olmayan sakinleri filtrele
            ]
            
            # Hesaplamaları yap
            records, total_cost = BosKonutController.calculate_empty_housing_costs(
                year=yil,
                month=ay,
                daire_listesi=daire_listesi,
                blok_listesi=blok_listesi,
                lojman_listesi=lojman_listesi,
                gider_kayitlari=gider_kayitlari,
                sakin_listesi=sakin_listesi
            )
            
            # Sonuçları tabloya ekle
            if records:
                for record in records:
                    self.bos_konut_tree.insert("", "end", values=(
                        record['sira_no'],
                        record['daire_adi'],
                        record['daire_no'],
                        f"{record['alan']:.2f}" if record['alan'] else "0.00",
                        BosKonutController.format_date(record['ilk_tarih']),
                        BosKonutController.format_date(record['son_tarih']),
                        record['sorumlu_gun_sayisi'],
                        BosKonutController.format_currency(record['konut_aidat_bedeli'])
                    ), tags=("bos",))
                
                # Toplam maliyet satırı ekle
                self.bos_konut_tree.insert("", "end", values=(
                    "",
                    "TOPLAM",
                    "",
                    "",
                    "",
                    "",
                    "",
                    BosKonutController.format_currency(total_cost)
                ), tags=("toplam",))
            else:
                # Boş konut yoksa bilgi mesajı
                self.bos_konut_tree.insert("", "end", values=(
                    "",
                    "Seçilen dönemde boş konut bulunmamaktadır",
                    "",
                    "",
                    "",
                    "",
                    "",
                    ""
                ))
            
            # Tag'ları ayarla
            self.bos_konut_tree.tag_configure("bos", background="#fff3cd")
            self.bos_konut_tree.tag_configure("toplam", background="#d4edda", font=("TkDefaultFont", 9, "bold"))
            
        except Exception as e:
            self.show_error(f"Boş konut listesi yüklenirken hata oluştu: {str(e)}")
