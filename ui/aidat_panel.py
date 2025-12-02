"""
Aidat paneli
"""

import customtkinter as ctk
from tkinter import ttk, Menu, Toplevel, filedialog
import tkinter as tk
from typing import List, Optional
from datetime import datetime
from ui.base_panel import BasePanel
from ui.error_handler import (
    ErrorHandler, handle_exception, show_error, show_success, show_warning,
    UIValidator
)
from controllers.aidat_controller import AidatIslemController, AidatOdemeController
from controllers.daire_controller import DaireController
from controllers.finans_islem_controller import FinansIslemController
from controllers.hesap_controller import HesapController
from controllers.kategori_yonetim_controller import KategoriYonetimController
from controllers.belge_controller import BelgeController
from models.base import AidatIslem, AidatOdeme, Daire
from models.exceptions import (
    ValidationError, DatabaseError, NotFoundError, DuplicateError, BusinessLogicError
)


class AidatPanel(BasePanel):
    """Aidat yönetimi paneli
    
    Aidat işlemleri ve ödeme takibi yönetimini sağlar.
    İki sekmeden oluşur: İşlemler ve Takip
    
    Attributes:
        aidat_islem_controller (AidatIslemController): Aidat işlem denetleyicisi
        aidat_odeme_controller (AidatOdemeController): Aidat ödeme denetleyicisi
        daire_controller (DaireController): Daire yönetim denetleyicisi
        finans_controller (FinansIslemController): Finansal işlem denetleyicisi
        hesap_controller (HesapController): Hesap yönetim denetleyicisi
        kategori_controller (KategoriYonetimController): Kategori yönetim denetleyicisi
        belge_controller (BelgeController): Belge yönetim denetleyicisi
    """

    def __init__(self, parent: ctk.CTk, colors: dict) -> None:
        self.aidat_islem_controller = AidatIslemController()
        self.aidat_odeme_controller = AidatOdemeController()
        self.daire_controller = DaireController()
        self.finans_controller = FinansIslemController()
        self.hesap_controller = HesapController()
        self.kategori_controller = KategoriYonetimController()
        self.belge_controller = BelgeController()
        self.secili_belge_yolu: Optional[str] = None

        # Veri saklama
        self.aidat_islemleri: List[AidatIslem] = []
        self.aidat_odemeleri: List[AidatOdeme] = []
        self.daireler: List[Daire] = []
        self.tum_aidat_islemleri_verisi: List[AidatIslem] = []  # Tüm işlemlerin orijinal listesi
        self.tum_aidat_odemeleri_verisi: List[AidatOdeme] = []  # Tüm ödemelerin orijinal listesi
        
        # Filtre değişkenleri - Aidat İşlemleri
        self.filter_islem_daire = "Tümü"
        self.filter_islem_aciklama = ""
        self.filter_islem_tarih_from = None
        self.filter_islem_tarih_to = None
        
        # Filtre değişkenleri - Aidat Takip
        self.filter_odeme_daire = "Tümü"
        self.filter_odeme_durum = "Tümü"
        self.filter_odeme_aciklama = ""

        super().__init__(parent, "💳 Aidat Yönetimi", colors)

    def setup_ui(self) -> None:
        """UI'yi oluştur"""
        # Ana container
        main_frame = ctk.CTkFrame(self.frame, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab kontrolü
        self.tabview = ctk.CTkTabview(main_frame, width=1000, height=600)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab'ları oluştur
        self.tabview.add("Aidat İşlemleri")
        self.tabview.add("Aidat Takip")

        # Tab içeriklerini oluştur
        self.setup_aidat_islemleri_tab()
        self.setup_aidat_takip_tab()

        # Başlangıç verilerini yükle
        try:
            self.load_data()
        except Exception as e:
            # Veritabanı henüz hazır değilse sessizce geç
            print(f"Veri yükleme hatası (normal): {e}")
            pass

    def setup_aidat_islemleri_tab(self) -> None:
        """Aidat işlemleri tab'ı"""
        tab = self.tabview.tab("Aidat İşlemleri")

        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Yeni aidat işlemi ekleme butonu
        add_button = ctk.CTkButton(
            main_frame,
            text="➕ Yeni Aidat İşlemi Ekle",
            command=self.open_yeni_aidat_islem_modal,
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"],
            height=40
        )
        add_button.pack(pady=(10, 5))

        # Tablo frame
        table_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        table_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Aidat işlemleri tablosu
        self.aidat_islem_tree = ttk.Treeview(
            table_frame,
            columns=("id", "daire", "sakin", "yil", "ay", "aidat_tutari", "katki_payi",
                    "elektrik", "su", "isinma", "ek_giderler", "toplam", "aciklama", "son_odeme"),
            show="headings",
            height=15
        )

        # Kolon başlıkları
        self.aidat_islem_tree.heading("id", text="ID")
        self.aidat_islem_tree.heading("daire", text="Daire")
        self.aidat_islem_tree.heading("sakin", text="Sakin")
        self.aidat_islem_tree.heading("yil", text="Yıl")
        self.aidat_islem_tree.heading("ay", text="Ay")
        self.aidat_islem_tree.heading("aidat_tutari", text="Aidat Tutarı")
        self.aidat_islem_tree.heading("katki_payi", text="Katkı Payı")
        self.aidat_islem_tree.heading("elektrik", text="Elektrik")
        self.aidat_islem_tree.heading("su", text="Su")
        self.aidat_islem_tree.heading("isinma", text="Isınma")
        self.aidat_islem_tree.heading("ek_giderler", text="Ek Giderler")
        self.aidat_islem_tree.heading("toplam", text="Toplam")
        self.aidat_islem_tree.heading("aciklama", text="Açıklama")
        self.aidat_islem_tree.heading("son_odeme", text="Son Ödeme")

        # Kolon genişlikleri ve hizalanması
        self.aidat_islem_tree.column("id", width=30, anchor="center")
        self.aidat_islem_tree.column("daire", width=200, anchor="center")
        self.aidat_islem_tree.column("sakin", width=120, anchor="center")
        self.aidat_islem_tree.column("yil", width=45, anchor="center")
        self.aidat_islem_tree.column("ay", width=45, anchor="center")
        self.aidat_islem_tree.column("aidat_tutari", width=60, anchor="center")
        self.aidat_islem_tree.column("katki_payi", width=60, anchor="center")
        self.aidat_islem_tree.column("elektrik", width=60, anchor="center")
        self.aidat_islem_tree.column("su", width=60, anchor="center")
        self.aidat_islem_tree.column("isinma", width=60, anchor="center")
        self.aidat_islem_tree.column("ek_giderler", width=60, anchor="center")
        self.aidat_islem_tree.column("toplam", width=75, anchor="center")
        self.aidat_islem_tree.column("aciklama", width=150, anchor="center")
        self.aidat_islem_tree.column("son_odeme", width=60, anchor="center")

        # Scrollbar
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.aidat_islem_tree.yview)
        self.aidat_islem_tree.configure(yscrollcommand=v_scrollbar.set)

        # Grid layout
        self.aidat_islem_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Sağ tık menüsü
        self.aidat_islem_context_menu = Menu(tab, tearoff=0)
        self.aidat_islem_context_menu.add_command(label="Düzenle", command=self.duzenle_aidat_islem)
        self.aidat_islem_context_menu.add_command(label="Sil", command=self.sil_aidat_islem)

        self.aidat_islem_tree.bind("<Button-3>", self.show_aidat_islem_context_menu)
        
        # Filtreleme paneli (alt taraf)
        self.setup_islem_filtreleme_paneli(main_frame)

    def setup_aidat_takip_tab(self) -> None:
        """Aidat takip tab'ı"""
        tab = self.tabview.tab("Aidat Takip")

        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tablo frame
        table_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Aidat ödemeleri tablosu
        self.aidat_odeme_tree = ttk.Treeview(
            table_frame,
            columns=("id", "daire", "tutar", "son_odeme", "odeme_tarihi", "durum"),
            show="headings",
            height=18
        )

        # Kolon başlıkları
        self.aidat_odeme_tree.heading("id", text="ID")
        self.aidat_odeme_tree.heading("daire", text="Daire")
        self.aidat_odeme_tree.heading("tutar", text="Tutar")
        self.aidat_odeme_tree.heading("son_odeme", text="Son Ödeme Tarihi")
        self.aidat_odeme_tree.heading("odeme_tarihi", text="Ödeme Tarihi")
        self.aidat_odeme_tree.heading("durum", text="Durum")

        # Kolon genişlikleri ve hizalanması
        self.aidat_odeme_tree.column("id", width=50, anchor="center")
        self.aidat_odeme_tree.column("daire", width=150, anchor="center")
        self.aidat_odeme_tree.column("tutar", width=100, anchor="center")
        self.aidat_odeme_tree.column("son_odeme", width=120, anchor="center")
        self.aidat_odeme_tree.column("odeme_tarihi", width=120, anchor="center")
        self.aidat_odeme_tree.column("durum", width=100, anchor="center")

        # Scrollbar
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.aidat_odeme_tree.yview)
        self.aidat_odeme_tree.configure(yscrollcommand=v_scrollbar.set)

        # Renkli satırlar için style tanımla
        style = ttk.Style()
        style.configure("gecmis.Treeview", foreground="#FF6B6B")
        style.configure("gecmis.Treeview.Heading", foreground="white")
        self.aidat_odeme_tree.tag_configure("gecmis", foreground="#FF6B6B")
        self.aidat_odeme_tree.tag_configure("odenmiş", foreground="#51CF66")
        self.aidat_odeme_tree.tag_configure("ödenmemiş", foreground="#FF6B6B")

        # Grid layout
        self.aidat_odeme_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Sağ tık menüsü
        self.aidat_odeme_context_menu = Menu(tab, tearoff=0)
        self.aidat_odeme_context_menu.add_command(label="Ödendi Olarak İşaretle", command=self.odeme_yap)
        self.aidat_odeme_context_menu.add_command(label="Ödenmedi Olarak İşaretle", command=self.odeme_iptal)

        self.aidat_odeme_tree.bind("<Button-3>", self.show_aidat_odeme_context_menu)
        
        # Filtreleme paneli (alt taraf)
        self.setup_odeme_filtreleme_paneli(main_frame)

    def get_sakin_at_date(self, daire_id: int, yil: int, ay: int) -> Optional[str]:
        """Verilen tarihte dairede yaşayan sakinin adını getir
        
        Args:
            daire_id (int): Daire ID'si
            yil (int): Yıl
            ay (int): Ay (1-12)
        
        Returns:
            Optional[str]: Sakin adı ya da None
        """
        try:
            from datetime import datetime
            from database.config import get_db
            from models.base import Sakin
            
            # İşlem tarihi
            islem_tarihi = datetime(yil, ay, 1)
            
            db = get_db()
            # Dairede tahsis tarihi <= işlem tarihi ve (çıkış tarihi None veya >= işlem tarihi) olan sakinleri bul
            sakin = db.query(Sakin).filter(
                Sakin.daire_id == daire_id,
                Sakin.tahsis_tarihi <= islem_tarihi,
                (Sakin.cikis_tarihi == None) | (Sakin.cikis_tarihi >= islem_tarihi)
            ).order_by(Sakin.tahsis_tarihi.desc()).first()
            
            # Eski daire olarak kayıtlı sakinleri de kontrol et (çıkış sonrası)
            if not sakin:
                sakin = db.query(Sakin).filter(
                    Sakin.eski_daire_id == daire_id,
                    Sakin.tahsis_tarihi <= islem_tarihi,
                    (Sakin.cikis_tarihi == None) | (Sakin.cikis_tarihi >= islem_tarihi)
                ).order_by(Sakin.tahsis_tarihi.desc()).first()
            
            db.close()
            return sakin.tam_ad if sakin else None
        except Exception as e:
            print(f"Sakin sorgulama hatası: {e}")
            return None

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_aidat_islemleri()
        self.load_aidat_odemeleri()
        self.load_daireler()

    def load_aidat_islemleri(self) -> None:
        """Aidat işlemlerini yükle"""
        for item in self.aidat_islem_tree.get_children():
            self.aidat_islem_tree.delete(item)

        self.aidat_islemleri = self.aidat_islem_controller.get_all_with_details()
        
        # ID'ye göre sırala (en son eklenen en üstte)
        self.aidat_islemleri = sorted(self.aidat_islemleri, key=lambda x: x.id, reverse=True)
        
        # Tüm işlemleri sakla (filtreleme için)
        self.tum_aidat_islemleri_verisi = self.aidat_islemleri.copy()
        
        # Filtre combo'larını güncelle
        if hasattr(self, 'filter_islem_daire_combo'):
            daire_listesi = set()
            yil_listesi = set()
            ay_listesi = set()
            for islem in self.aidat_islemleri:
                daire_info = f"{islem.daire.blok.lojman.ad} {islem.daire.blok.ad}-{islem.daire.daire_no}"
                daire_listesi.add(daire_info)
                yil_listesi.add(str(islem.yil))
                ay_listesi.add(islem.ay_adi)
            daire_options = ["Tümü"] + sorted(list(daire_listesi))
            yil_options = ["Tümü"] + sorted(list(yil_listesi), reverse=True)
            ay_options = ["Tümü"] + sorted(list(ay_listesi))
            self.filter_islem_daire_combo.configure(values=daire_options)
            self.filter_islem_yil_combo.configure(values=yil_options)
            self.filter_islem_ay_combo.configure(values=ay_options)

        for islem in self.aidat_islemleri:
            daire_info = f"{islem.daire.blok.lojman.ad} {islem.daire.blok.ad}-{islem.daire.daire_no}"
            # İşlem tarihinde dairede oturan sakinini bul
            sakin_info = self.get_sakin_at_date(islem.daire.id, islem.yil, islem.ay) or "Boş"
            
            # İlişkili finans işleminden para birimini al
            para_birimi = "₺"  # Varsayılan
            for odeme in islem.odemeler:
                if odeme.finans_islem and odeme.finans_islem.hesap:
                    para_birimi = odeme.finans_islem.hesap.para_birimi or "₺"
                    break

            self.aidat_islem_tree.insert("", "end", values=(
                islem.id,
                daire_info,
                sakin_info,
                islem.yil,
                islem.ay_adi,
                f"{islem.aidat_tutari:.2f} {para_birimi}",
                f"{islem.katki_payi:.2f} {para_birimi}",
                f"{islem.elektrik:.2f} {para_birimi}",
                f"{islem.su:.2f} {para_birimi}",
                f"{islem.isinma:.2f} {para_birimi}",
                f"{islem.ek_giderler:.2f} {para_birimi}",
                f"{islem.toplam_tutar:.2f} {para_birimi}",
                islem.aciklama or "",
                islem.son_odeme_tarihi.strftime("%d.%m.%Y") if islem.son_odeme_tarihi else ""
            ))

    def load_aidat_odemeleri(self) -> None:
        """Aidat ödemelerini yükle"""
        for item in self.aidat_odeme_tree.get_children():
            self.aidat_odeme_tree.delete(item)

        # Hem ödenmiş hem ödenmemiş ödemeleri getir
        odemeler = []
        odemeler.extend(self.aidat_odeme_controller.get_odeme_bekleyenler())
        odemeler.extend(self.aidat_odeme_controller.get_odeme_yapilanlar())

        # Benzersiz ID'lere göre sırala
        seen_ids = set()
        unique_odemeler = []
        for odeme in sorted(odemeler, key=lambda x: x.id):
            if odeme.id not in seen_ids:
                unique_odemeler.append(odeme)
                seen_ids.add(odeme.id)

        # ID'ye göre sırala (en son eklenen en üstte)
        unique_odemeler = sorted(unique_odemeler, key=lambda x: x.id, reverse=True)

        self.aidat_odemeleri = unique_odemeler
        
        # Tüm ödemeleri sakla (filtreleme için)
        self.tum_aidat_odemeleri_verisi = self.aidat_odemeleri.copy()
        
        # Daire ve durum filtre combo'larını güncelle
        if hasattr(self, 'filter_odeme_daire_combo'):
            daire_listesi = set()
            durum_listesi = set()
            for odeme in self.aidat_odemeleri:
                daire_info = ""
                if odeme.aidat_islem and odeme.aidat_islem.daire:
                    daire = odeme.aidat_islem.daire
                    daire_info = f"{daire.blok.lojman.ad} {daire.blok.ad}-{daire.daire_no}"
                    daire_listesi.add(daire_info)
                durum_listesi.add(odeme.durum)
            
            daire_options = ["Tümü"] + sorted(list(daire_listesi))
            durum_options = ["Tümü"] + sorted(list(durum_listesi))
            self.filter_odeme_daire_combo.configure(values=daire_options)
            self.filter_odeme_durum_combo.configure(values=durum_options)

        for odeme in self.aidat_odemeleri:
            daire_info = ""
            para_birimi = "₺"  # Varsayılan
            
            if odeme.aidat_islem and odeme.aidat_islem.daire:
                daire = odeme.aidat_islem.daire
                daire_info = f"{daire.blok.lojman.ad} {daire.blok.ad}-{daire.daire_no}"
                
                # İlişkili finans işleminden para birimini al
                if odeme.finans_islem and odeme.finans_islem.hesap:
                    para_birimi = odeme.finans_islem.hesap.para_birimi or "₺"

            # Renk kodlaması: Ödendi ise yeşil, ödenmedi ve geçmiş tarih ise kırmızı
            tag = ""
            if odeme.odendi:
                tag = "odenmiş"
            elif odeme.son_odeme_tarihi and odeme.son_odeme_tarihi.date() < datetime.now().date():
                tag = "gecmis"
            
            self.aidat_odeme_tree.insert("", "end", values=(
                odeme.id,
                daire_info,
                f"{odeme.tutar:.2f} {para_birimi}",
                odeme.son_odeme_tarihi.strftime("%d.%m.%Y") if odeme.son_odeme_tarihi else "",
                odeme.odeme_tarihi.strftime("%d.%m.%Y") if odeme.odeme_tarihi else "",
                odeme.durum
            ), tags=(tag,) if tag else ())

    def load_daireler(self) -> None:
        """Daireleri yükle"""
        self.daireler = self.daire_controller.get_all_with_details()

    # Context menu handlers
    def show_aidat_islem_context_menu(self, event: tk.Event) -> None:
        try:
            self.aidat_islem_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.aidat_islem_context_menu.grab_release()

    def show_aidat_odeme_context_menu(self, event: tk.Event) -> None:
        try:
            self.aidat_odeme_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.aidat_odeme_context_menu.grab_release()

    # Aidat işlemi işlemleri
    def duzenle_aidat_islem(self) -> None:
        """Seçili aidat işlemini düzenle"""
        selected = self.aidat_islem_tree.selection()
        if not selected:
            self.show_error("Düzenlemek için bir aidat işlemi seçiniz!")
            return
        
        selected_id = int(self.aidat_islem_tree.item(selected[0])["values"][0])
        
        # İşlemi bul
        islem = None
        for i in self.aidat_islemleri:
            if i.id == selected_id:
                islem = i
                break
        
        if not islem:
            self.show_error("Seçilen aidat işlemi bulunamadı!")
            return
        
        # Ödeme durumunu kontrol et
        if islem.odemeler:
            for odeme in islem.odemeler:
                if odeme.odendi:
                    self.show_error("Ödenmesi kaydedilmiş aidat işlemleri düzenlenemez!")
                    return
        
        self.load_daireler()
        self.open_aidat_islem_modal(islem)

    def sil_aidat_islem(self) -> None:
        """Seçili aidat işlemini sil"""
        selected = self.aidat_islem_tree.selection()
        if not selected:
            self.show_error("Silmek için bir aidat işlemi seçiniz!")
            return
        
        selected_id = int(self.aidat_islem_tree.item(selected[0])["values"][0])
        
        # İşlemi bul
        islem = None
        for i in self.aidat_islemleri:
            if i.id == selected_id:
                islem = i
                break
        
        if not islem:
            self.show_error("Seçilen aidat işlemi bulunamadı!")
            return
        
        # Ödeme durumunu kontrol et
        if islem.odemeler:
            for odeme in islem.odemeler:
                if odeme.odendi:
                    self.show_error("Ödenmesi kaydedilmiş aidat işlemleri silinemez!")
                    return
        
        # Onay iste
        from tkinter import messagebox
        if messagebox.askyesno("Onay", f"Bu aidat işlemini silmek istediğinizden emin misiniz?\n\n{islem.daire.blok.lojman.ad} {islem.daire.blok.ad}-{islem.daire.daire_no} ({islem.ay_adi} {islem.yil})"):
            try:
                # Aidatı sil
                self.aidat_islem_controller.delete(islem.id)
                self.show_message("Aidat işlemi silindi!")
                self.load_data()
            except Exception as e:
                self.show_error(f"Silme işlemi sırasında hata: {str(e)}")

    # Aidat ödeme işlemleri
    def odeme_yap(self) -> None:
        """Seçili ödemeyi ödendi olarak işaretle ve gelir işlemi ekle"""
        selected = self.aidat_odeme_tree.selection()
        if not selected:
            self.show_error("Ödemeyi işaretlemek için bir kayıt seçiniz!")
            return
        
        selected_id = int(self.aidat_odeme_tree.item(selected[0])["values"][0])
        
        # Ödemeyi bul
        odeme = None
        for o in self.aidat_odemeleri:
            if o.id == selected_id:
                odeme = o
                break
        
        if not odeme:
            self.show_error("Seçilen ödeme bulunamadı!")
            return
        
        if odeme.odendi:
            self.show_error("Bu ödeme zaten ödendi olarak işaretlenmiş!")
            return
        
        self.open_odeme_gelir_modal(odeme)

    def odeme_iptal(self) -> None:
       """Seçili ödemeyi ödenmedi olarak işaretle"""
       selected = self.aidat_odeme_tree.selection()
       if not selected:
           self.show_error("Ödemeyi işaretlemek için bir kayıt seçiniz!")
           return
       
       selected_id = int(self.aidat_odeme_tree.item(selected[0])["values"][0])
       
       # Ödemeyi bul
       odeme = None
       for o in self.aidat_odemeleri:
           if o.id == selected_id:
               odeme = o
               break
       
       if not odeme:
           self.show_error("Seçilen ödeme bulunamadı!")
           return
       
       if not odeme.odendi:
           self.show_error("Bu ödeme zaten ödenmedi olarak işaretlenmiş!")
           return
       
       try:
           # Ödeme iptali yap
           self.aidat_odeme_controller.odeme_iptal(odeme.id)
           self.show_message("Ödeme iptal edildi!")
           self.load_data()
       except Exception as e:
           self.show_error(f"İptal işlemi sırasında hata: {str(e)}")

    # Modal açma fonksiyonları
    def open_yeni_aidat_islem_modal(self) -> None:
        """Yeni aidat işlemi ekleme modal'ı"""
        # Daireleri yükle
        self.load_daireler()
        self.open_aidat_islem_modal(None)

    def open_aidat_islem_modal(self, islem: Optional[AidatIslem] = None) -> None:
        """Aidat işlemi ekleme/düzenleme modal'ı"""
        # Modal pencere
        modal = ctk.CTkToplevel(self.frame)
        modal.title("Yeni Aidat İşlemi Ekle" if islem is None else "Aidat İşlemi Düzenle")
        modal.resizable(False, False)
        
        # Sabit konumlandırma (ekran ortasında)
        modal.geometry("450x500+475+175")
        modal.transient(self.frame)
        modal.lift()
        modal.focus_force()

        # Başlık
        title_label = ctk.CTkLabel(
            modal,
            text="Yeni Aidat İşlemi Ekle" if islem is None else "Aidat İşlemi Düzenle",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(20, 10))

        # Scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(modal, fg_color=self.colors["surface"])
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Daire seçimi
        daire_label = ctk.CTkLabel(scrollable_frame, text="Daire:", text_color=self.colors["text"])
        daire_label.pack(anchor="w", padx=20, pady=(20, 5))

        daire_options = []
        for daire in self.daireler:
            daire_text = f"{daire.blok.lojman.ad} {daire.blok.ad}-{daire.daire_no}"
            daire_options.append(daire_text)

        if not daire_options:
            daire_options = ["Daire bulunamadı - Önce daire ekleyin"]

        # Daire seçimi değiştiğinde aidat tutarını ve katkı payını otomatik olarak doldur
        def on_daire_selected(value: Optional[str] = None) -> None:
            selected_daire_text = daire_combo.get()
            if selected_daire_text and selected_daire_text != "Daire bulunamadı - Önce daire ekleyin":
                for daire in self.daireler:
                    daire_text = f"{daire.blok.lojman.ad} {daire.blok.ad}-{daire.daire_no}"
                    if daire_text == selected_daire_text:
                        # Aidat tutarını doldur
                        aidat_entry.delete(0, "end")
                        aidat_val = daire.guncel_aidat if daire.guncel_aidat else 0
                        aidat_entry.insert(0, str(aidat_val))
                        
                        # Katkı payını doldur
                        katki_entry.delete(0, "end")
                        katki_val = daire.katki_payi if daire.katki_payi else 0
                        katki_entry.insert(0, str(katki_val))
                        
                        # Toplam tutarı yeniden hesapla
                        hesapla_toplam()
                        break

        daire_combo = ctk.CTkComboBox(scrollable_frame, values=daire_options, command=on_daire_selected)
        daire_combo.pack(fill="x", padx=20, pady=(0, 15))
        
        # Varsayılan seçim
        default_selection = None
        if islem and islem.daire:
            # Mevcut işlemse düzenlenen işlemin dairesini seç
            selected_daire = f"{islem.daire.blok.lojman.ad} {islem.daire.blok.ad}-{islem.daire.daire_no}"
            if selected_daire in daire_options:
                default_selection = selected_daire
                daire_combo.set(selected_daire)
        elif daire_options and daire_options[0] != "Daire bulunamadı - Önce daire ekleyin":
            # Yeni işlemse ilk daiyi seç
            default_selection = daire_options[0]
            daire_combo.set(default_selection)

        # Yıl ve Ay
        year_month_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.colors["background"])
        year_month_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Yıl
        year_label = ctk.CTkLabel(year_month_frame, text="Yıl:", text_color=self.colors["text"])
        year_label.pack(side="left", padx=(0, 10))

        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 2, current_year + 3)]
        year_combo = ctk.CTkComboBox(year_month_frame, values=years, width=100)
        year_combo.pack(side="left", padx=(0, 20))
        year_combo.set(str(current_year))
        if islem:
            year_combo.set(str(islem.yil))

        # Ay
        month_label = ctk.CTkLabel(year_month_frame, text="Ay:", text_color=self.colors["text"])
        month_label.pack(side="left", padx=(0, 10))

        months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                 "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        month_combo = ctk.CTkComboBox(year_month_frame, values=months, width=120)
        month_combo.pack(side="left")
        month_combo.set(months[datetime.now().month - 1])
        if islem:
            month_combo.set(months[islem.ay - 1])

        # Aidat tutarı
        aidat_label = ctk.CTkLabel(scrollable_frame, text="Aidat Tutarı (₺):", text_color=self.colors["text"])
        aidat_label.pack(anchor="w", padx=20, pady=(0, 5))

        aidat_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 500.00")
        aidat_entry.pack(fill="x", padx=20, pady=(0, 15))
        if islem:
            aidat_entry.insert(0, str(islem.aidat_tutari or 0))

        # Katkı payı
        katki_label = ctk.CTkLabel(scrollable_frame, text="Katkı Payı (₺):", text_color=self.colors["text"])
        katki_label.pack(anchor="w", padx=20, pady=(0, 5))

        katki_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 100.00")
        katki_entry.pack(fill="x", padx=20, pady=(0, 15))
        if islem:
            katki_entry.insert(0, str(islem.katki_payi or 0))

        # Toplam tutarı hesapla fonksiyonu (burada tanımla, on_daire_selected öncesinde)
        def hesapla_toplam(*args: tuple) -> None:
            try:
                aidat = float(aidat_entry.get() or 0)
                katki = float(katki_entry.get() or 0)
                elektrik = float(elektrik_entry.get() or 0)
                su = float(su_entry.get() or 0)
                isinma = float(isinma_entry.get() or 0)
                ek = float(ek_gider_entry.get() or 0)

                toplam = aidat + katki + elektrik + su + isinma + ek
                toplam_value.configure(text=f"{toplam:.2f}")
            except ValueError:
                toplam_value.configure(text="0.00")

         # Elektrik
        elektrik_label = ctk.CTkLabel(scrollable_frame, text="Elektrik (₺):", text_color=self.colors["text"])
        elektrik_label.pack(anchor="w", padx=20, pady=(0, 5))

        elektrik_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 50.00")
        elektrik_entry.pack(fill="x", padx=20, pady=(0, 15))
        if islem:
            elektrik_entry.insert(0, str(islem.elektrik or 0))

        # Su
        su_label = ctk.CTkLabel(scrollable_frame, text="Su (₺):", text_color=self.colors["text"])
        su_label.pack(anchor="w", padx=20, pady=(0, 5))

        su_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 30.00")
        su_entry.pack(fill="x", padx=20, pady=(0, 15))
        if islem:
            su_entry.insert(0, str(islem.su or 0))

        # Isınma
        isinma_label = ctk.CTkLabel(scrollable_frame, text="Isınma (₺):", text_color=self.colors["text"])
        isinma_label.pack(anchor="w", padx=20, pady=(0, 5))

        isinma_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 80.00")
        isinma_entry.pack(fill="x", padx=20, pady=(0, 15))
        if islem:
            isinma_entry.insert(0, str(islem.isinma or 0))

        # Ek giderler
        ek_gider_label = ctk.CTkLabel(scrollable_frame, text="Ek Giderler (₺):", text_color=self.colors["text"])
        ek_gider_label.pack(anchor="w", padx=20, pady=(0, 5))

        ek_gider_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 25.00")
        ek_gider_entry.pack(fill="x", padx=20, pady=(0, 15))
        if islem:
            ek_gider_entry.insert(0, str(islem.ek_giderler or 0))

        # Toplam tutar (hesaplanacak)
        toplam_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.colors["background"])
        toplam_frame.pack(fill="x", padx=20, pady=(0, 15))

        toplam_label = ctk.CTkLabel(toplam_frame, text="Toplam Tutar (₺):", text_color=self.colors["text"])
        toplam_label.pack(side="left")

        toplam_value = ctk.CTkLabel(toplam_frame, text="0.00", text_color=self.colors["success"],
                                   font=ctk.CTkFont(weight="bold"))
        toplam_value.pack(side="right")

        # Son ödeme tarihi
        tarih_label = ctk.CTkLabel(scrollable_frame, text="Son Ödeme Tarihi:", text_color=self.colors["text"])
        tarih_label.pack(anchor="w", padx=20, pady=(0, 5))

        tarih_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="GG.AA.YYYY")
        tarih_entry.pack(fill="x", padx=20, pady=(0, 15))
        if islem and islem.son_odeme_tarihi:
            tarih_entry.insert(0, islem.son_odeme_tarihi.strftime("%d.%m.%Y"))
        else:
            # Bir sonraki ayın 16'una varsayılan tarih
            next_month = datetime.now().replace(day=16)
            if datetime.now().day > 16:
                next_month = next_month.replace(month=next_month.month + 1)
            tarih_entry.insert(0, next_month.strftime("%d.%m.%Y"))

        # Açıklama
        aciklama_label = ctk.CTkLabel(scrollable_frame, text="Açıklama (Opsiyonel):", text_color=self.colors["text"])
        aciklama_label.pack(anchor="w", padx=20, pady=(0, 5))

        aciklama_textbox = ctk.CTkTextbox(scrollable_frame, height=60)
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
            command=lambda: self.save_aidat_islem(
                modal, islem, daire_combo.get(), year_combo.get(), month_combo.get(),
                aidat_entry.get(), katki_entry.get(), elektrik_entry.get(), su_entry.get(),
                isinma_entry.get(), ek_gider_entry.get(), tarih_entry.get(), aciklama_textbox.get("1.0", "end")
            ),
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"]
        )
        save_button.pack(side="right")

        # Entry'lere değişiklik event'i ekle
        for entry in [aidat_entry, katki_entry, elektrik_entry, su_entry, isinma_entry, ek_gider_entry]:
            entry.bind("<KeyRelease>", hesapla_toplam)

        # İlk hesapla
        hesapla_toplam()
        on_daire_selected()

    def save_aidat_islem(self, modal: ctk.CTkToplevel, existing_islem: Optional[AidatIslem], daire_secim: str, yil: str, ay_str: str,
                        aidat_tutari: str, katki_payi: str, elektrik: str, su: str, isinma: str, ek_giderler: str,
                        son_odeme_tarihi: str, aciklama: str) -> None:
        """Aidat işlemini kaydet - ErrorHandler ile"""
        # Önce işlemi yap, sonra modal'ı kapat ve verileri yenile
        try:
            with ErrorHandler(parent=modal, show_success_msg=False):
                # Validasyonlar
                if daire_secim == "Daire bulunamadı - Önce daire ekleyin":
                    raise ValidationError(
                        "Geçerli bir daire seçilmelidir",
                        code="VAL_001"
                    )

                # Daire'yi bul
                daire = None
                for d in self.daireler:
                    daire_text = f"{d.blok.lojman.ad} {d.blok.ad}-{d.daire_no}"
                    if daire_text == daire_secim:
                        daire = d
                        break

                if not daire:
                    raise NotFoundError(
                        "Seçilen daire bulunamadı",
                        code="NOT_FOUND_001"
                    )

                # Yıl ve ay parse
                try:
                    yil_int = int(yil)
                    ay_int = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                             "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"].index(ay_str) + 1
                except (ValueError, IndexError):
                    raise ValidationError(
                        "Geçersiz yıl veya ay",
                        code="VAL_002"
                    )

                # Tutarları parse
                try:
                    aidat_val = float(aidat_tutari or 0)
                    katki_val = float(katki_payi or 0)
                    elektrik_val = float(elektrik or 0)
                    su_val = float(su or 0)
                    isinma_val = float(isinma or 0)
                    ek_val = float(ek_giderler or 0)
                    toplam_val = aidat_val + katki_val + elektrik_val + su_val + isinma_val + ek_val
                except ValueError:
                    raise ValidationError(
                        "Tutar alanları geçerli sayılar olmalıdır",
                        code="VAL_002"
                    )

                # Son ödeme tarihi parse
                try:
                    tarih_obj = datetime.strptime(son_odeme_tarihi.strip(), "%d.%m.%Y")
                except ValueError:
                    raise ValidationError(
                        "Son ödeme tarihi GG.AA.YYYY formatında olmalıdır",
                        code="VAL_006"
                    )

                # Toplam tutarın 0'dan büyük olması gerekir
                if toplam_val <= 0:
                    raise ValidationError(
                        "Toplam tutar 0'dan büyük olmalıdır",
                        code="VAL_005",
                        details={"tutar": toplam_val}
                    )

                # AidatIslem oluştur veya güncelle
                if existing_islem:
                    # Güncelle
                    islem_data = {
                        "yil": yil_int,
                        "ay": ay_int,
                        "daire_id": daire.id,
                        "aidat_tutari": aidat_val,
                        "katki_payi": katki_val,
                        "elektrik": elektrik_val,
                        "su": su_val,
                        "isinma": isinma_val,
                        "ek_giderler": ek_val,
                        "toplam_tutar": toplam_val,
                        "son_odeme_tarihi": tarih_obj,
                        "aciklama": aciklama.strip() if aciklama else None
                    }
                    self.aidat_islem_controller.update(existing_islem.id, islem_data)
                    
                    # Aidat ödemesini de güncelle
                    if existing_islem.odemeler:
                        for odeme in existing_islem.odemeler:
                            odeme_data = {
                                "tutar": toplam_val,
                                "son_odeme_tarihi": tarih_obj
                            }
                            self.aidat_odeme_controller.update(odeme.id, odeme_data)
                    
                    action = "güncellendi"
                else:
                    # Yeni oluştur
                    islem_data = {
                        "yil": yil_int,
                        "ay": ay_int,
                        "daire_id": daire.id,
                        "aidat_tutari": aidat_val,
                        "katki_payi": katki_val,
                        "elektrik": elektrik_val,
                        "su": su_val,
                        "isinma": isinma_val,
                        "ek_giderler": ek_val,
                        "toplam_tutar": toplam_val,
                        "son_odeme_tarihi": tarih_obj,
                        "aciklama": aciklama.strip() if aciklama else None
                    }
                    created_islem = self.aidat_islem_controller.create(islem_data)
                    
                    # AidatOdeme kaydı oluştur (otomatik olarak)
                    odeme_data = {
                        "aidat_islem_id": created_islem.id,
                        "tutar": toplam_val,
                        "son_odeme_tarihi": tarih_obj,
                        "odendi": False,
                        "aciklama": None
                    }
                    self.aidat_odeme_controller.create(odeme_data)
                    
                    action = "eklendi"

                # Başarı mesajı göster
                show_success(parent=modal, title="Başarılı", message=f"Aidat işlemi {action}! Toplam: {toplam_val:.2f} ₺")

            # Modal'ı kapat (error handler dışında)
            modal.destroy()

            # Listeyi yenile (error handler dışında)
            self.load_data()
            
        except Exception as e:
            # Modal hala varsa ve hata oluştuysa modal'ı kapat
            if modal.winfo_exists():
                modal.destroy()
            # Hatayı yeniden fırlat ki üst seviye error handler işleyebilsin
            raise

    def open_odeme_gelir_modal(self, odeme: AidatOdeme) -> None:
        """Aidat ödemesini ödendi olarak işaretle ve gelir işlemi oluştur (Yeni Gelir Ekle modalı gibi)"""
        # Modal pencere
        modal = ctk.CTkToplevel(self.frame)
        modal.title("💰 Yeni Gelir Ekle - Aidat Ödemesi")
        modal.resizable(False, False)
        
        # Sabit konumlandırma (ekran ortasında)
        modal.geometry("450x500+475+175")
        modal.transient(self.frame)
        modal.lift()
        modal.focus_force()

        # Ana frame
        main_frame = ctk.CTkFrame(modal, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text="💰 Yeni Aidat Geliri Ekle",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["success"]
        )
        title_label.pack(pady=(20, 30))

        # Form alanı - Scrollable frame ile aşağı kaydırma desteği
        form_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=self.colors["background"],
            height=300
        )
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Tarih
        tarih_label = ctk.CTkLabel(form_frame, text="Tarih:", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        tarih_label.pack(anchor="w", padx=20, pady=(20, 5))

        tarih_frame = ctk.CTkFrame(form_frame, fg_color=self.colors["surface"], height=35)
        tarih_frame.pack(fill="x", padx=20, pady=(0, 15))
        tarih_frame.pack_propagate(False)

        tarih_entry = ctk.CTkEntry(tarih_frame, placeholder_text="GG.AA.YYYY", border_width=0, fg_color="transparent")
        tarih_entry.pack(side="left", fill="x", expand=True, padx=10)

        bugun_btn = ctk.CTkButton(
            tarih_frame,
            text="📅 Bugün",
            width=80,
            height=25,
            font=ctk.CTkFont(size=10),
            command=lambda: tarih_entry.delete(0, tk.END) or tarih_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        )
        bugun_btn.pack(side="right", padx=(5, 10))

        # Varsayılan tarih (son ödeme tarihi)
        if odeme.son_odeme_tarihi:
            tarih_entry.insert(0, odeme.son_odeme_tarihi.strftime("%d.%m.%Y"))
        else:
            tarih_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Ana kategori
        ana_kategoriler = self.kategori_controller.get_ana_kategoriler()
        ana_kategori_options = [kat.name for kat in ana_kategoriler if hasattr(kat, 'tip') and kat.tip == "gelir"]
        
        ana_kategori_label = ctk.CTkLabel(form_frame, text="Ana Kategori:", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        ana_kategori_label.pack(anchor="w", padx=20, pady=(0, 5))

        ana_kategori_combo = ctk.CTkComboBox(
            form_frame,
            values=["Seçiniz"] + (ana_kategori_options if ana_kategori_options else []),
            font=ctk.CTkFont(size=12),
            height=35
        )
        ana_kategori_combo.pack(fill="x", padx=20, pady=(0, 15))
        ana_kategori_combo.set("Seçiniz")

        # Alt kategori
        alt_kategori_label = ctk.CTkLabel(form_frame, text="Alt Kategori (Opsiyonel):", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        alt_kategori_label.pack(anchor="w", padx=20, pady=(0, 5))

        alt_kategori_combo = ctk.CTkComboBox(
            form_frame,
            values=["Seçiniz"],
            font=ctk.CTkFont(size=12),
            height=35
        )
        alt_kategori_combo.pack(fill="x", padx=20, pady=(0, 15))
        alt_kategori_combo.set("Seçiniz")

        # Ana kategori değiştiğinde alt kategorileri güncelle
        def on_ana_kategori_change(selected: str) -> None:
            try:
                if selected == "Seçiniz":
                    alt_kategori_combo.configure(values=["Seçiniz"])
                    alt_kategori_combo.set("Seçiniz")
                else:
                    ana_kat = next((kat for kat in ana_kategoriler if kat.name == selected), None)
                    if ana_kat:
                        alt_kategoriler = [alt.name for alt in ana_kat.alt_kategoriler if hasattr(alt, 'aktif') and alt.aktif]
                        alt_kategori_combo.configure(values=["Seçiniz"] + alt_kategoriler)
                        alt_kategori_combo.set("Seçiniz")
            except Exception as e:
                print(f"Kategori değişim hatası: {e}")

        ana_kategori_combo.configure(command=on_ana_kategori_change)

        # Hesap
        hesap_label = ctk.CTkLabel(form_frame, text="Hesap:", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        hesap_label.pack(anchor="w", padx=20, pady=(0, 5))

        aktif_hesaplar = self.hesap_controller.get_aktif_hesaplar()
        hesap_options = [f"{h.ad} ({h.tur})" for h in aktif_hesaplar]
        if not hesap_options:
            hesap_options = ["Aktif hesap bulunamadı - Önce hesap ekleyin"]
        else:
            hesap_options.insert(0, "Seçiniz")

        hesap_combo = ctk.CTkComboBox(
            form_frame,
            values=hesap_options,
            font=ctk.CTkFont(size=12),
            height=35
        )
        hesap_combo.pack(fill="x", padx=20, pady=(0, 15))

        # Varsayılan hesabı seç
        varsayilan_hesap = next((h for h in aktif_hesaplar if h.varsayilan), None) if aktif_hesaplar else None
        if varsayilan_hesap:
            hesap_combo.set(f"{varsayilan_hesap.ad} ({varsayilan_hesap.tur})")
        else:
            hesap_combo.set("Seçiniz")

        # Tutar
        tutar_label = ctk.CTkLabel(form_frame, text="Tutar (₺):", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        tutar_label.pack(anchor="w", padx=20, pady=(0, 5))

        tutar_entry = ctk.CTkEntry(form_frame, placeholder_text="Örn: 1500.00")
        tutar_entry.pack(fill="x", padx=20, pady=(0, 15))
        tutar_entry.insert(0, str(odeme.tutar))

        # Açıklama
        aciklama_label = ctk.CTkLabel(form_frame, text="Açıklama (Opsiyonel):", font=ctk.CTkFont(weight="bold"), text_color=self.colors["text"])
        aciklama_label.pack(anchor="w", padx=20, pady=(0, 5))

        aciklama_textbox = ctk.CTkTextbox(
            form_frame,
            height=60,
            font=ctk.CTkFont(size=11)
        )
        aciklama_textbox.pack(fill="x", padx=20, pady=(0, 15))

        # Varsayılan açıklama
        if odeme.aidat_islem and odeme.aidat_islem.daire:
            daire_info = f"{odeme.aidat_islem.daire.blok.lojman.ad} {odeme.aidat_islem.daire.blok.ad}-{odeme.aidat_islem.daire.daire_no}"
            default_aciklama = f"{daire_info} aidat ödemesi"
            aciklama_textbox.insert("1.0", default_aciklama)

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
        self.secili_belge_yolu = None

        # Belge butonları frame'i
        belge_buttons_frame = ctk.CTkFrame(form_frame, fg_color=self.colors["background"])
        belge_buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Belge seç butonu
        belge_sec_btn = ctk.CTkButton(
            belge_buttons_frame,
            text="📁 Belge Seç",
            command=lambda: self.sec_belge(),
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            height=30,
            width=100,
            font=ctk.CTkFont(size=10, weight="bold")
        )
        belge_sec_btn.pack(side="left", padx=(0, 5))

        # Belgeyi sil butonu
        self.belge_sil_btn = ctk.CTkButton(
            belge_buttons_frame,
            text="🗑️ Sil",
            command=lambda: self.sil_secili_belge(),
            fg_color=self.colors["error"],
            hover_color=self.colors["text_secondary"],
            height=30,
            width=100,
            font=ctk.CTkFont(size=10, weight="bold"),
            state="disabled"
        )
        self.belge_sil_btn.pack(side="left", padx=(0, 5))

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
            state="disabled"
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
            command=lambda: self.save_odeme_gelir(
                modal, odeme, tarih_entry.get(), ana_kategori_combo.get(), alt_kategori_combo.get(), 
                hesap_combo.get(), tutar_entry.get(), aciklama_textbox.get("1.0", "end").strip()
            ),
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"],
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_button.pack(side="right")

    def save_odeme_gelir(self, modal: ctk.CTkToplevel, odeme: AidatOdeme, tarih_str: str, ana_kat_str: str, alt_kat_str: str, hesap_str: str, tutar_str: str, aciklama: str) -> None:
        """Ödeme ve gelir işlemini kaydet"""
        # Tarih validasyonu
        try:
            tarih_obj = datetime.strptime(tarih_str.strip(), "%d.%m.%Y")
        except ValueError:
            show_error(parent=modal, title="Hata", message="Tarih GG.AA.YYYY formatında olmalıdır!")
            return

        # Hesap validasyonu
        hesap_ad = hesap_str.split(" (")[0]
        hesaplar = self.hesap_controller.get_aktif_hesaplar()
        hesap = next((h for h in hesaplar if h.ad == hesap_ad), None)
        if not hesap:
            show_error(parent=modal, title="Hata", message="Geçerli bir hesap seçilmelidir!")
            return

        # Tutar validasyonu
        try:
            tutar = float(tutar_str.strip())
            if tutar <= 0:
                show_error(parent=modal, title="Hata", message="Tutar pozitif sayı olmalıdır!")
                return
        except ValueError:
            show_error(parent=modal, title="Hata", message="Tutar geçerli bir sayı olmalıdır!")
            return

        try:
            with ErrorHandler(parent=modal, show_success_msg=False):
                # Create a single session for both operations
                from database.config import get_db
                from sqlalchemy.orm import Session
                db: Session = get_db()
                
                try:
                    # Kategoriyi bul
                    kategori_id = None
                    if alt_kat_str and alt_kat_str != "Seçiniz":
                        # Alt kategori seçilmişse
                        ana_kategoriler = self.kategori_controller.get_ana_kategoriler()
                        for ana_kat in ana_kategoriler:
                            for alt_kat in ana_kat.alt_kategoriler:
                                if alt_kat.name == alt_kat_str:
                                    kategori_id = alt_kat.id
                                    break

                    # 1. Gelir işlemi oluştur
                    finans_data = {
                        "tur": "Gelir",
                        "tarih": tarih_obj,
                        "tutar": float(tutar),
                        "hesap_id": hesap.id,
                        "aciklama": aciklama if aciklama else "Aidat ödemesi",
                        "kategori_id": kategori_id,
                        "ana_kategori_text": ana_kat_str if ana_kat_str and ana_kat_str != "Seçiniz" else "Aidat Geliri",
                        "belge_yolu": self.secili_belge_yolu
                    }
                    
                    finans_islem = self.finans_controller.create(finans_data, db)
                    finans_islem_id = finans_islem.id

                    # 2. Ödeme yapıldı olarak işaretle ve finans kaydı ID'sini bağla
                    self.aidat_odeme_controller.odeme_yap(odeme.id, tarih_obj, finans_islem_id, db)

                    # Modal'ı kapat SONRA mesaj göster
                    modal.destroy()
                    show_success(parent=self.parent, title="Başarılı", message="Ödeme kaydı oluşturuldu ve gelir işlemi eklendi!")

                    # Listeyi yenile
                    self.load_data()
                finally:
                    db.close()
                    
        except (ValidationError, DatabaseError, NotFoundError, BusinessLogicError) as e:
            handle_exception(e, parent=modal)
        except Exception as e:
            handle_exception(e, parent=modal)

    # Aidat İşlemleri Filtreleme
    def setup_islem_filtreleme_paneli(self, parent: ctk.CTkFrame) -> None:
        """Aidat işlemleri filtreleme panelini oluştur"""
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
        
        # Daire filtresi
        daire_label = ctk.CTkLabel(
            filters_container,
            text="Daire:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        daire_label.pack(side="left", padx=(0, 8))
        
        self.filter_islem_daire_combo = ctk.CTkComboBox(
            filters_container,
            values=["Tümü"],
            command=lambda v: self.uygula_islem_filtreler(),
            width=150,
            height=28,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=10)
        )
        self.filter_islem_daire_combo.set("Tümü")
        self.filter_islem_daire_combo.pack(side="left", padx=(0, 20))
        
        # Yıl filtresi
        yil_label = ctk.CTkLabel(
            filters_container,
            text="Yıl:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        yil_label.pack(side="left", padx=(0, 8))
        
        self.filter_islem_yil_combo = ctk.CTkComboBox(
            filters_container,
            values=["Tümü"],
            command=lambda v: self.uygula_islem_filtreler(),
            width=80,
            height=28,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=10)
        )
        self.filter_islem_yil_combo.set("Tümü")
        self.filter_islem_yil_combo.pack(side="left", padx=(0, 20))
        
        # Ay filtresi
        ay_label = ctk.CTkLabel(
            filters_container,
            text="Ay:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        ay_label.pack(side="left", padx=(0, 8))
        
        self.filter_islem_ay_combo = ctk.CTkComboBox(
            filters_container,
            values=["Tümü"],
            command=lambda v: self.uygula_islem_filtreler(),
            width=100,
            height=28,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=10)
        )
        self.filter_islem_ay_combo.set("Tümü")
        self.filter_islem_ay_combo.pack(side="left", padx=(0, 20))
        
        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filters_container,
            text="🔄 Temizle",
            command=self.temizle_islem_filtreler,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=10, weight="bold"),
            height=28,
            width=80,
            corner_radius=4
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def uygula_islem_filtreler(self) -> None:
        """Aidat işlemleri sekmesine seçili filtreleri uygula"""
        try:
            # Treeview'i temizle
            for item in self.aidat_islem_tree.get_children():
                self.aidat_islem_tree.delete(item)
            
            # Filtre değerlerini al
            filter_daire = self.filter_islem_daire_combo.get()
            filter_yil = self.filter_islem_yil_combo.get()
            filter_ay = self.filter_islem_ay_combo.get()
            
            # Tüm işlemleri filtrele
            for islem in self.tum_aidat_islemleri_verisi:
                daire_info = f"{islem.daire.blok.lojman.ad} {islem.daire.blok.ad}-{islem.daire.daire_no}"
                
                # Daire filtresi
                if filter_daire != "Tümü" and daire_info != filter_daire:
                    continue
                
                # Yıl filtresi
                if filter_yil != "Tümü" and str(islem.yil) != filter_yil:
                    continue
                
                # Ay filtresi
                if filter_ay != "Tümü" and islem.ay_adi != filter_ay:
                    continue
                
                # İşlemi tabloya ekle
                # İşlem tarihinde dairede oturan sakinini bul
                sakin_info = self.get_sakin_at_date(islem.daire.id, islem.yil, islem.ay) or "Boş"
                
                # İlişkili finans işleminden para birimini al
                para_birimi = "₺"  # Varsayılan
                for odeme in islem.odemeler:
                    if odeme.finans_islem and odeme.finans_islem.hesap:
                        para_birimi = odeme.finans_islem.hesap.para_birimi or "₺"
                        break

                self.aidat_islem_tree.insert("", "end", values=(
                    islem.id,
                    daire_info,
                    sakin_info,
                    islem.yil,
                    islem.ay_adi,
                    f"{islem.aidat_tutari:.2f} {para_birimi}",
                    f"{islem.katki_payi:.2f} {para_birimi}",
                    f"{islem.elektrik:.2f} {para_birimi}",
                    f"{islem.su:.2f} {para_birimi}",
                    f"{islem.isinma:.2f} {para_birimi}",
                    f"{islem.ek_giderler:.2f} {para_birimi}",
                    f"{islem.toplam_tutar:.2f} {para_birimi}",
                    islem.aciklama or "",
                    islem.son_odeme_tarihi.strftime("%d.%m.%Y") if islem.son_odeme_tarihi else ""
                ))
        except Exception as e:
            print(f"İşlem filtreleme hatası: {e}")

    def temizle_islem_filtreler(self) -> None:
        """Aidat işlemleri filtreleri temizle ve tümünü göster"""
        self.filter_islem_daire_combo.set("Tümü")
        self.filter_islem_yil_combo.set("Tümü")
        self.filter_islem_ay_combo.set("Tümü")
        self.uygula_islem_filtreler()

    # Aidat Takip Filtreleme
    def setup_odeme_filtreleme_paneli(self, parent: ctk.CTkFrame) -> None:
        """Aidat takip (ödeme) filtreleme panelini oluştur"""
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
        
        # Daire filtresi
        daire_label = ctk.CTkLabel(
            filters_container,
            text="Daire:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        daire_label.pack(side="left", padx=(0, 8))
        
        self.filter_odeme_daire_combo = ctk.CTkComboBox(
            filters_container,
            values=["Tümü"],
            command=lambda v: self.uygula_odeme_filtreler(),
            width=150,
            height=28,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=10)
        )
        self.filter_odeme_daire_combo.set("Tümü")
        self.filter_odeme_daire_combo.pack(side="left", padx=(0, 20))
        
        # Durum filtresi
        durum_label = ctk.CTkLabel(
            filters_container,
            text="Durum:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        durum_label.pack(side="left", padx=(0, 8))
        
        self.filter_odeme_durum_combo = ctk.CTkComboBox(
            filters_container,
            values=["Tümü"],
            command=lambda v: self.uygula_odeme_filtreler(),
            width=130,
            height=28,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=10)
        )
        self.filter_odeme_durum_combo.set("Tümü")
        self.filter_odeme_durum_combo.pack(side="left", padx=(0, 20))
        
        # Açıklama araması
        aciklama_label = ctk.CTkLabel(
            filters_container,
            text="Açıklama:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        aciklama_label.pack(side="left", padx=(0, 8))
        
        self.filter_odeme_aciklama_entry = ctk.CTkEntry(
            filters_container,
            placeholder_text="Ara...",
            width=130,
            height=28,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.filter_odeme_aciklama_entry.pack(side="left", padx=(0, 20))
        self.filter_odeme_aciklama_entry.bind("<KeyRelease>", lambda e: self.uygula_odeme_filtreler())
        
        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filters_container,
            text="🔄 Temizle",
            command=self.temizle_odeme_filtreler,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=10, weight="bold"),
            height=28,
            width=80,
            corner_radius=4
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def uygula_odeme_filtreler(self) -> None:
        """Aidat takip sekmesine seçili filtreleri uygula"""
        try:
            # Treeview'i temizle
            for item in self.aidat_odeme_tree.get_children():
                self.aidat_odeme_tree.delete(item)
            
            # Filtre değerlerini al
            filter_daire = self.filter_odeme_daire_combo.get()
            filter_durum = self.filter_odeme_durum_combo.get()
            filter_aciklama = self.filter_odeme_aciklama_entry.get().lower()
            
            # Tüm ödemeleri filtrele
            for odeme in self.tum_aidat_odemeleri_verisi:
                daire_info = ""
                if odeme.aidat_islem and odeme.aidat_islem.daire:
                    daire = odeme.aidat_islem.daire
                    daire_info = f"{daire.blok.lojman.ad} {daire.blok.ad}-{daire.daire_no}"
                
                # Daire filtresi
                if filter_daire != "Tümü" and daire_info != filter_daire:
                    continue
                
                # Durum filtresi
                if filter_durum != "Tümü" and odeme.durum != filter_durum:
                    continue
                
                # Açıklama filtresi
                aciklama = (odeme.aciklama or "").lower()
                if filter_aciklama and filter_aciklama not in aciklama:
                    continue
                
                # Ödemeyi tabloya ekle
                para_birimi = "₺"  # Varsayılan
                if odeme.finans_islem and odeme.finans_islem.hesap:
                    para_birimi = odeme.finans_islem.hesap.para_birimi or "₺"
                
                # Renk kodlaması: Ödendi ise yeşil, ödenmedi ve geçmiş tarih ise kırmızı
                tag = ""
                if odeme.odendi:
                    tag = "odenmiş"
                elif odeme.son_odeme_tarihi and odeme.son_odeme_tarihi.date() < datetime.now().date():
                    tag = "gecmis"
                
                self.aidat_odeme_tree.insert("", "end", values=(
                    odeme.id,
                    daire_info,
                    f"{odeme.tutar:.2f} {para_birimi}",
                    odeme.son_odeme_tarihi.strftime("%d.%m.%Y") if odeme.son_odeme_tarihi else "",
                    odeme.odeme_tarihi.strftime("%d.%m.%Y") if odeme.odeme_tarihi else "",
                    odeme.durum
                ), tags=(tag,) if tag else ())
        except Exception as e:
            print(f"Ödeme filtreleme hatası: {e}")

    def temizle_odeme_filtreler(self) -> None:
        """Aidat takip filtreleri temizle ve tümünü göster"""
        self.filter_odeme_daire_combo.set("Tümü")
        self.filter_odeme_durum_combo.set("Tümü")
        self.filter_odeme_aciklama_entry.delete(0, "end")
        self.uygula_odeme_filtreler()

    # Belge yönetim metodları
    def sec_belge(self) -> None:
        """Belge seç"""
        belge_yolu = filedialog.askopenfilename(
            title="Belge Seç",
            filetypes=[
                ("Tüm Dosyalar", "*.*"),
                ("PDF", "*.pdf"),
                ("Görseller", "*.png *.jpg *.jpeg *.gif"),
                ("Word", "*.docx *.doc"),
                ("Excel", "*.xlsx *.xls")
            ]
        )
        
        if belge_yolu:
            self.secili_belge_yolu = belge_yolu
            dosya_adi = self.belge_controller.dosya_adi_al(belge_yolu)
            self.belge_durumu_label.configure(text=f"✓ Belge: {dosya_adi}")
            self.belge_sil_btn.configure(state="normal")
            self.belge_ac_btn.configure(state="normal")

    def sil_secili_belge(self) -> None:
        """Seçili belgeyi sil"""
        self.secili_belge_yolu = None
        self.belge_durumu_label.configure(text="Belge seçilmedi")
        self.belge_sil_btn.configure(state="disabled")
        self.belge_ac_btn.configure(state="disabled")

    def ac_secili_belge(self) -> None:
        """Seçili belgeyi aç"""
        if self.secili_belge_yolu:
            try:
                import os
                import subprocess
                if os.path.exists(self.secili_belge_yolu):
                    if os.name == 'nt':  # Windows
                        os.startfile(self.secili_belge_yolu)
                    else:  # Linux/Mac
                        subprocess.Popen(['xdg-open', self.secili_belge_yolu])
            except Exception as e:
                self.show_error(f"Belge açılırken hata: {str(e)}")
