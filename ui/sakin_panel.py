"""
Sakin paneli
"""

import customtkinter as ctk
from tkinter import ttk, Menu, Toplevel
import tkinter as tk
from typing import List, Optional, Any
from datetime import datetime
from ui.base_panel import BasePanel
from ui.error_handler import (
    ErrorHandler, handle_exception, show_error, show_success, show_warning,
    UIValidator
)
from controllers.sakin_controller import SakinController
from controllers.daire_controller import DaireController
from models.base import Sakin, Daire
from models.exceptions import (
    ValidationError, DatabaseError, NotFoundError, DuplicateError
)
from models.validation import Validator


class SakinPanel(BasePanel):
    """Sakin yönetimi paneli
    
    Sakin (kiracı) kayıtlarının yönetimini sağlar.
    Aktif sakinler ve arşiv (geçmiş sakinler) olmak üzere iki sekmeye ayrılmıştır.
    
    Attributes:
        sakin_controller (SakinController): Sakin yönetim denetleyicisi
        daire_controller (DaireController): Daire yönetim denetleyicisi
        aktif_sakinler (List[Sakin]): Aktif sakinler listesi
        pasif_sakinler (List[Sakin]): Arşiv sakinleri listesi
        daireler (List[Daire]): Daire nesneleri listesi
    """

    def __init__(self, parent: Any, colors: dict) -> None:
        self.sakin_controller = SakinController()
        self.daire_controller = DaireController()

        # Veri saklama
        self.aktif_sakinler: List[Sakin] = []
        self.pasif_sakinler: List[Sakin] = []
        self.daireler: List[Daire] = []
        
        # Filtre değişkenleri
        self.filter_aktif_ad_soyad = ""
        self.filter_aktif_daire = "Tümü"
        self.filter_pasif_ad_soyad = ""
        self.filter_pasif_daire = "Tümü"

        super().__init__(parent, "👥 Sakin Yönetimi", colors)

    def _normalize_param(self, param: Any, is_date: bool = False) -> str:
        """Parametreyi string'e normalize et (datetime, int, None vb.)
        
        Args:
            param (Any): Normalize edilecek parametre
            is_date (bool): Tarih parametresi mi (varsayılan: False)
        
        Returns:
            str: Normalize edilmiş string değer
        """
        if param is None:
            return ""
        if is_date and hasattr(param, 'strftime'):
            return str(param.strftime("%d.%m.%Y"))
        return str(param).strip()

    def setup_ui(self) -> None:
        """UI'yi oluştur"""
        # Ana container
        main_frame = ctk.CTkFrame(self.frame, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Yeni sakin ekleme butonu (üstte)
        add_button = ctk.CTkButton(
            main_frame,
            text="➕ Yeni Sakin Ekle",
            command=self.open_yeni_sakin_modal,
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"],
            height=40
        )
        add_button.pack(pady=(10, 5))

        # Tab kontrolü
        self.tabview = ctk.CTkTabview(main_frame, width=900, height=550)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Tab'ları oluştur
        self.tabview.add("Aktif Sakinler")
        self.tabview.add("Arşiv")

        # Tab içeriklerini oluştur
        self.setup_aktif_sakinler_tab()
        self.setup_arsiv_tab()

        # Başlangıç verilerini yükle
        self.load_data()

    def setup_aktif_sakinler_tab(self) -> None:
        """Aktif sakinler tab'ı"""
        tab = self.tabview.tab("Aktif Sakinler")

        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text="Aktif Sakinler",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(10, 5), fill="x")

        # Treeview container
        tree_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Sakin listesi
        self.aktif_sakin_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "ad_soyad", "rutbe", "daire", "telefon", "email", "aile_sayisi", "tahsis_tarihi", "giris_tarihi", "notlar"),
            show="headings",
            height=15
        )

        # Kolon başlıkları
        self.aktif_sakin_tree.heading("id", text="ID")
        self.aktif_sakin_tree.heading("ad_soyad", text="Ad Soyad")
        self.aktif_sakin_tree.heading("rutbe", text="Rütbe/Ünvan")
        self.aktif_sakin_tree.heading("daire", text="Daire")
        self.aktif_sakin_tree.heading("telefon", text="Telefon")
        self.aktif_sakin_tree.heading("email", text="E-posta")
        self.aktif_sakin_tree.heading("aile_sayisi", text="Aile Birey Sayısı")
        self.aktif_sakin_tree.heading("tahsis_tarihi", text="Tahsis Tarihi")
        self.aktif_sakin_tree.heading("giris_tarihi", text="Giriş Tarihi")
        self.aktif_sakin_tree.heading("notlar", text="Notlar")

        # Kolon genişlikleri ve ortalaması
        self.aktif_sakin_tree.column("id", width=10, anchor="center")
        self.aktif_sakin_tree.column("ad_soyad", width=120, anchor="center")
        self.aktif_sakin_tree.column("rutbe", width=60, anchor="center")
        self.aktif_sakin_tree.column("daire", width=170, anchor="center")
        self.aktif_sakin_tree.column("telefon", width=40, anchor="center")
        self.aktif_sakin_tree.column("email", width=150, anchor="center")
        self.aktif_sakin_tree.column("aile_sayisi", width=40, anchor="center")
        self.aktif_sakin_tree.column("tahsis_tarihi", width=30, anchor="center")
        self.aktif_sakin_tree.column("giris_tarihi", width=30, anchor="center")
        self.aktif_sakin_tree.column("notlar", width=150, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.aktif_sakin_tree.yview)
        self.aktif_sakin_tree.configure(yscrollcommand=scrollbar.set)

        self.aktif_sakin_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Filtre paneli
        self.setup_aktif_filtre_paneli(main_frame)

        # Sağ tık menüsü
        self.aktif_context_menu = Menu(main_frame, tearoff=0)
        self.aktif_context_menu.add_command(label="Düzenle", command=self.duzenle_sakin)
        self.aktif_context_menu.add_command(label="Pasif Yap", command=self.pasif_yap_sakin)

        self.aktif_sakin_tree.bind("<Button-3>", self.show_aktif_context_menu)

    def setup_arsiv_tab(self) -> None:
        """Arşiv tab'ı"""
        tab = self.tabview.tab("Arşiv")

        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text="Pasif Sakinler (Arşiv)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_secondary"]
        )
        title_label.pack(pady=(10, 5), fill="x")

        # Treeview container
        tree_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Sakin listesi
        self.pasif_sakin_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "ad_soyad", "rutbe", "daire", "telefon", "email", "aile_sayisi", "tahsis_tarihi", "giris_tarihi", "cikis_tarihi"),
            show="headings",
            height=15
        )

        # Kolon başlıkları
        self.pasif_sakin_tree.heading("id", text="ID")
        self.pasif_sakin_tree.heading("ad_soyad", text="Ad Soyad")
        self.pasif_sakin_tree.heading("rutbe", text="Rütbe/Ünvan")
        self.pasif_sakin_tree.heading("daire", text="Daire")
        self.pasif_sakin_tree.heading("telefon", text="Telefon")
        self.pasif_sakin_tree.heading("email", text="E-posta")
        self.pasif_sakin_tree.heading("aile_sayisi", text="Aile Birey Sayısı")
        self.pasif_sakin_tree.heading("tahsis_tarihi", text="Tahsis Tarihi")
        self.pasif_sakin_tree.heading("giris_tarihi", text="Giriş Tarihi")
        self.pasif_sakin_tree.heading("cikis_tarihi", text="Çıkış Tarihi")

        # Kolon genişlikleri ve ortalaması
        self.pasif_sakin_tree.column("id", width=20, anchor="center")
        self.pasif_sakin_tree.column("ad_soyad", width=120, anchor="center")
        self.pasif_sakin_tree.column("rutbe", width=60, anchor="center")
        self.pasif_sakin_tree.column("daire", width=170, anchor="center")
        self.pasif_sakin_tree.column("telefon", width=40, anchor="center")
        self.pasif_sakin_tree.column("email", width=150, anchor="center")
        self.pasif_sakin_tree.column("aile_sayisi", width=30, anchor="center")
        self.pasif_sakin_tree.column("tahsis_tarihi", width=30, anchor="center")
        self.pasif_sakin_tree.column("giris_tarihi", width=30, anchor="center")
        self.pasif_sakin_tree.column("cikis_tarihi", width=30, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.pasif_sakin_tree.yview)
        self.pasif_sakin_tree.configure(yscrollcommand=scrollbar.set)

        self.pasif_sakin_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Filtre paneli
        self.setup_pasif_filtre_paneli(main_frame)

        # Sağ tık menüsü
        self.pasif_context_menu = Menu(main_frame, tearoff=0)
        self.pasif_context_menu.add_command(label="Düzenle", command=self.duzenle_sakin)
        self.pasif_context_menu.add_command(label="Sil", command=self.sil_sakin_pasif)
        self.pasif_context_menu.add_command(label="Aktif Yap", command=self.aktif_yap_sakin)

        self.pasif_sakin_tree.bind("<Button-3>", self.show_pasif_context_menu)

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_aktif_sakinler()
        self.load_pasif_sakinler()
        self.load_daireler()

    def load_aktif_sakinler(self) -> None:
        """Aktif sakinleri yükle"""
        try:
            # Treeview'i temizle
            for item in self.aktif_sakin_tree.get_children():
                self.aktif_sakin_tree.delete(item)

            self.aktif_sakinler = self.sakin_controller.get_aktif_sakinler()

            # Daire listesini güncelle
            if hasattr(self, 'filter_aktif_daire_combo'):
                daire_listesi = set()
                for sakin in self.aktif_sakinler:
                    if sakin.daire:
                        daire_info = f"{sakin.daire.blok.lojman.ad} {sakin.daire.blok.ad}-{sakin.daire.daire_no}"
                        daire_listesi.add(daire_info)
                daire_options = ["Tümü"] + sorted(list(daire_listesi))
                self.filter_aktif_daire_combo.configure(values=daire_options)

            # Tüm verileri yükle
            for sakin in self.aktif_sakinler:
                daire_info = ""
                if sakin.daire:
                    daire_info = f"{sakin.daire.blok.lojman.ad} {sakin.daire.blok.ad}-{sakin.daire.daire_no}"

                self.aktif_sakin_tree.insert("", "end", values=(
                    sakin.id,
                    sakin.ad_soyad,
                    sakin.rutbe_unvan or "",
                    daire_info,
                    sakin.telefon or "",
                    sakin.email or "",
                    sakin.aile_birey_sayisi,
                    sakin.tahsis_tarihi.strftime("%d.%m.%Y") if sakin.tahsis_tarihi else "",
                    sakin.giris_tarihi.strftime("%d.%m.%Y") if sakin.giris_tarihi else "",
                    sakin.notlar or ""
                ))
        except DatabaseError as e:
            show_error(parent=self.frame, title="Veritabanı Hatası", message=str(e.message))
        except Exception as e:
            show_error(parent=self.frame, title="Hata", message=f"Aktif sakinler yüklenirken hata oluştu: {str(e)}")

    def load_pasif_sakinler(self) -> None:
        """Pasif sakinleri yükle"""
        try:
            # Treeview'i temizle
            for item in self.pasif_sakin_tree.get_children():
                self.pasif_sakin_tree.delete(item)

            self.pasif_sakinler = self.sakin_controller.get_pasif_sakinler()

            # Daire listesini güncelle
            if hasattr(self, 'filter_pasif_daire_combo'):
                daire_listesi = set()
                for sakin in self.pasif_sakinler:
                    if sakin.daire:
                        daire_info = f"{sakin.daire.blok.lojman.ad} {sakin.daire.blok.ad}-{sakin.daire.daire_no}"
                        daire_listesi.add(daire_info)
                    elif sakin.eski_daire:
                        daire_info = f"{sakin.eski_daire.blok.lojman.ad} {sakin.eski_daire.blok.ad}-{sakin.eski_daire.daire_no}"
                        daire_listesi.add(daire_info)
                daire_options = ["Tümü"] + sorted(list(daire_listesi))
                self.filter_pasif_daire_combo.configure(values=daire_options)

            # Tüm verileri yükle
            for sakin in self.pasif_sakinler:
                daire_info = ""
                if sakin.daire:
                    daire_info = f"{sakin.daire.blok.lojman.ad} {sakin.daire.blok.ad}-{sakin.daire.daire_no}"
                elif sakin.eski_daire:
                    daire_info = f"{sakin.eski_daire.blok.lojman.ad} {sakin.eski_daire.blok.ad}-{sakin.eski_daire.daire_no}"

                self.pasif_sakin_tree.insert("", "end", values=(
                    sakin.id,
                    sakin.ad_soyad,
                    sakin.rutbe_unvan or "",
                    daire_info,
                    sakin.telefon or "",
                    sakin.email or "",
                    sakin.aile_birey_sayisi,
                    sakin.tahsis_tarihi.strftime("%d.%m.%Y") if sakin.tahsis_tarihi else "",
                    sakin.giris_tarihi.strftime("%d.%m.%Y") if sakin.giris_tarihi else "",
                    sakin.cikis_tarihi.strftime("%d.%m.%Y") if sakin.cikis_tarihi else ""
                ))
        except DatabaseError as e:
            show_error(parent=self.frame, title="Veritabanı Hatası", message=str(e.message))
        except Exception as e:
            show_error(parent=self.frame, title="Hata", message=f"Pasif sakinler yüklenirken hata oluştu: {str(e)}")

    def load_daireler(self) -> None:
        """Daireleri yükle"""
        self.daireler = self.daire_controller.get_bos_daireler()

    def show_aktif_context_menu(self, event: Any) -> None:
        """Aktif sakinler için sağ tık menüsünü göster"""
        try:
            self.aktif_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.aktif_context_menu.grab_release()

    def show_pasif_context_menu(self, event: Any) -> None:
        """Pasif sakinler için sağ tık menüsünü göster"""
        try:
            self.pasif_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.pasif_context_menu.grab_release()

    def duzenle_sakin(self) -> None:
        """Seçili sakin'i düzenle"""
        # Seçili öğeyi al
        selected_tab = self.tabview.get()
        if selected_tab == "Aktif Sakinler":
            selection = self.aktif_sakin_tree.selection()
            if not selection:
                self.show_error("Lütfen düzenlenecek sakin'i seçin!")
                return
            sakin_id = self.aktif_sakin_tree.item(selection[0])['values'][0]
            sakin = next((s for s in self.aktif_sakinler if s.id == sakin_id), None)
        else:
            selection = self.pasif_sakin_tree.selection()
            if not selection:
                self.show_error("Lütfen düzenlenecek sakin'i seçin!")
                return
            sakin_id = self.pasif_sakin_tree.item(selection[0])['values'][0]
            sakin = next((s for s in self.pasif_sakinler if s.id == sakin_id), None)

        if sakin:
            self.open_duzenle_sakin_modal(sakin)

    def sil_sakin_pasif(self) -> None:
        """Pasif sekmesinden sakini kaldır (arayüzden gözükmez, veri korunur)
        
        Soft delete işlemi: Veritabanında veri kalır ama arayüzde gözükmez.
        Veri bütünlüğü ve denetim izi korunur.
        """
        selection = self.pasif_sakin_tree.selection()
        if not selection:
            self.show_error("Lütfen kaldırılacak sakin'i seçin!")
            return
        
        sakin_id = self.pasif_sakin_tree.item(selection[0])['values'][0]
        
        if self.ask_yes_no(f"Sakin #{sakin_id} arşivden kaldırılacak. Emin misiniz?\n(Veritabanında veri korunur)"):
            try:
                if self.sakin_controller.delete(int(sakin_id)):
                    self.show_message(f"Sakin #{sakin_id} başarıyla kaldırıldı! (Veri korunmuştur)")
                else:
                    self.show_error(f"Sakin #{sakin_id} bulunamadı!")
            except Exception as e:
                self.show_error(f"Sakin kaldırılırken hata oluştu: {str(e)}")
            self.load_data()

    def pasif_yap_sakin(self) -> None:
        """Seçili sakin'i pasif yap"""
        selection = self.aktif_sakin_tree.selection()
        if not selection:
            self.show_error("Lütfen pasif yapılacak sakin'i seçin!")
            return

        sakin_id = self.aktif_sakin_tree.item(selection[0])['values'][0]
        sakin = next((s for s in self.aktif_sakinler if s.id == sakin_id), None)
        
        if sakin:
            self.open_pasif_yap_modal(sakin)

    def open_pasif_yap_modal(self, sakin: Sakin) -> None:
        """Sakin pasifleştirme modal'ı"""
        # Modal pencere
        modal = ctk.CTkToplevel(self.frame)
        modal.title("Sakin'i Pasif Yap")
        modal.geometry("300x335")
        modal.transient(self.frame)
        modal.lift()
        modal.focus_force()

        # Başlık
        title_label = ctk.CTkLabel(
            modal,
            text="Sakin'i Pasif Yap",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["error"]
        )
        title_label.pack(pady=(20, 10))

        # Scrollable frame for content
        scrollable_frame = ctk.CTkScrollableFrame(modal, fg_color=self.colors["surface"])
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Sakin bilgisi
        sakin_info = ctk.CTkLabel(
            scrollable_frame,
            text=f"Sakin: {sakin.ad_soyad}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text"]
        )
        sakin_info.pack(anchor="w", padx=20, pady=(20, 20))

        # Ayrılış Tarihi
        tarih_label = ctk.CTkLabel(
            scrollable_frame,
            text="Ayrılış Tarihi (GG.AA.YYYY):",
            text_color=self.colors["text"]
        )
        tarih_label.pack(anchor="w", padx=20, pady=(0, 5))

        tarih_entry = ctk.CTkEntry(
            scrollable_frame,
            placeholder_text="GG.AA.YYYY"
        )
        tarih_entry.pack(fill="x", padx=20, pady=(0, 20))
        tarih_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Butonlar
        button_frame = ctk.CTkFrame(modal, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # İptal butonu
        cancel_button = ctk.CTkButton(
            button_frame,
            text="İptal",
            command=modal.destroy,
            fg_color=self.colors["text_secondary"],
            hover_color=self.colors["border"],
            width=100
        )
        cancel_button.pack(side="left", padx=(0, 10))

        # Pasif Yap butonu
        pasif_button = ctk.CTkButton(
            button_frame,
            text="Pasif Yap",
            command=lambda: self.validate_and_confirm_pasif_yap(modal, sakin.id, tarih_entry),
            fg_color=self.colors["primary"],
            hover_color=self.colors["text_secondary"],
            width=100
        )
        pasif_button.pack(side="right")

    def validate_and_confirm_pasif_yap(self, modal: Any, sakin_id: int, tarih_entry: Any) -> None:
        """UI validasyonlarını yap ve pasif yapma işlemini onayla"""
        # Tarih validasyonu
        cikis_tarih = tarih_entry.get().strip()
        if not cikis_tarih:
            show_error(parent=modal, title="Boş Alan", message="Ayrılış tarihi zorunludur!")
            tarih_entry.focus()
            return
            
        try:
            datetime.strptime(cikis_tarih, "%d.%m.%Y")
        except ValueError:
            show_error(parent=modal, title="Hata", message="Ayrılış tarihi GG.AA.YYYY formatında olmalıdır!")
            tarih_entry.focus()
            return
            
        # Validasyon başarılı, gerçek işlemi yap
        self.confirm_pasif_yap(modal, sakin_id, cikis_tarih)

    def confirm_pasif_yap(self, modal: Any, sakin_id: int, cikis_tarih: str) -> None:
        """Pasif yapma işlemini onayla"""
        try:
            if not cikis_tarih.strip():
                show_error(parent=modal, title="Eksik Alan", message="Ayrılış tarihi zorunludur!")
                return

            # Tarihi parse et
            try:
                cikis_tarihi = datetime.strptime(cikis_tarih.strip(), "%d.%m.%Y")
            except ValueError:
                show_error(parent=modal, title="Hata", message="Ayrılış tarihi GG.AA.YYYY formatında olmalıdır!")
                return

            # Pasif yap
            if self.sakin_controller.pasif_yap(sakin_id, cikis_tarihi):
                show_success(parent=modal, title="Başarılı", message=f"Sakin #{sakin_id} başarıyla pasif yapıldı!")
            else:
                show_error(parent=modal, title="Bulunamadı", message=f"Sakin #{sakin_id} bulunamadı!")
                return

        except NotFoundError as e:
            show_error(parent=modal, title="Bulunamadı", message=str(e.message))
            return
        except DatabaseError as e:
            show_error(parent=modal, title="Veritabanı Hatası", message=str(e.message))
            return
        except Exception as e:
            handle_exception(e, parent=modal)
            return

        # Modal'ı kapat
        modal.destroy()

        # Listeyi yenile
        self.load_data()

    def aktif_yap_sakin(self) -> None:
        """Seçili pasif sakin'i yeni aktif sakin olarak ekle"""
        selection = self.pasif_sakin_tree.selection()
        if not selection:
            self.show_error("Lütfen aktif yapılacak sakin'i seçin!")
            return

        sakin_id = self.pasif_sakin_tree.item(selection[0])['values'][0]
        pasif_sakin = next((s for s in self.pasif_sakinler if s.id == sakin_id), None)

        if pasif_sakin:
            self.open_aktif_yap_modal(pasif_sakin)

    def open_yeni_sakin_modal(self) -> None:
        """Yeni sakin ekleme modal'ını aç"""
        self.open_sakin_modal(None)

    def open_duzenle_sakin_modal(self, sakin: Sakin) -> None:
        """Sakin düzenleme modal'ını aç"""
        self.open_sakin_modal(sakin)

    def open_aktif_yap_modal(self, pasif_sakin: Sakin) -> None:
        """Pasif sakini yeni aktif sakin olarak ekleme modal'ı"""
        # Modal pencere
        modal = ctk.CTkToplevel(self.frame)
        modal.title("Sakin'i Tekrar Aktif Yap")
        modal.geometry("400x500")
        modal.transient(self.frame)
        modal.lift()
        modal.focus_force()

        # Başlık
        title_label = ctk.CTkLabel(
            modal,
            text="Sakin'i Tekrar Aktif Yap",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(20, 10))

        # Scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(modal, fg_color=self.colors["surface"])
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Form alanları
        # Ad Soyad
        ad_label = ctk.CTkLabel(scrollable_frame, text="Ad Soyad:", text_color=self.colors["text"])
        ad_label.pack(anchor="w", padx=20, pady=(20, 5))

        ad_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: Ahmet Yılmaz")
        ad_entry.pack(fill="x", padx=20, pady=(0, 15))
        ad_entry.insert(0, pasif_sakin.ad_soyad or "")

        # Rütbe/Ünvan
        rutbe_label = ctk.CTkLabel(scrollable_frame, text="Rütbesi/Ünvanı:", text_color=self.colors["text"])
        rutbe_label.pack(anchor="w", padx=20, pady=(0, 5))

        rutbe_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: Öğretmen")
        rutbe_entry.pack(fill="x", padx=20, pady=(0, 15))
        rutbe_entry.insert(0, pasif_sakin.rutbe_unvan or "")

        # Yeni Dairesi (Opsiyonel - arşiv sakini tekrar tahsis edilebilir)
        daire_label = ctk.CTkLabel(scrollable_frame, text="Yeni Dairesi:", text_color=self.colors["text"])
        daire_label.pack(anchor="w", padx=20, pady=(0, 5))

        # Daire seçeneklerini hazırla (aktif yapma için güncel boş daireler)
        daireler_list = self.daire_controller.get_bos_daireler()
        daire_options = ["Seçiniz..."]
        for daire in daireler_list:
            daire_str = f"{daire.blok.lojman.ad} {daire.blok.ad}-{daire.daire_no}"
            if daire_str not in daire_options:
                daire_options.append(daire_str)

        daire_combo = ctk.CTkComboBox(scrollable_frame, values=daire_options)
        daire_combo.pack(fill="x", padx=20, pady=(0, 15))
        daire_combo.set("Seçiniz...")

        # Telefon
        telefon_label = ctk.CTkLabel(scrollable_frame, text="Telefon:", text_color=self.colors["text"])
        telefon_label.pack(anchor="w", padx=20, pady=(0, 5))

        telefon_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 0532 123 45 67")
        telefon_entry.pack(fill="x", padx=20, pady=(0, 15))
        telefon_entry.insert(0, pasif_sakin.telefon or "")

        # E-posta
        email_label = ctk.CTkLabel(scrollable_frame, text="E-posta:", text_color=self.colors["text"])
        email_label.pack(anchor="w", padx=20, pady=(0, 5))

        email_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: ahmet.yilmaz@example.com")
        email_entry.pack(fill="x", padx=20, pady=(0, 15))
        email_entry.insert(0, pasif_sakin.email or "")

        # Aile Birey Sayısı
        aile_sayisi_label = ctk.CTkLabel(scrollable_frame, text="Aile Birey Sayısı:", text_color=self.colors["text"])
        aile_sayisi_label.pack(anchor="w", padx=20, pady=(0, 5))

        aile_sayisi_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 3")
        aile_sayisi_entry.pack(fill="x", padx=20, pady=(0, 15))
        aile_sayisi_entry.insert(0, pasif_sakin.aile_birey_sayisi or "")

        # Tahsis Tarihi
        tahsis_tarih_label = ctk.CTkLabel(scrollable_frame, text="Tahsis Tarihi (GG.AA.YYYY)", text_color=self.colors["text"])
        tahsis_tarih_label.pack(anchor="w", padx=20, pady=(0, 5))

        tahsis_tarih_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="GG.AA.YYYY")
        tahsis_tarih_entry.pack(fill="x", padx=20, pady=(0, 15))
        tahsis_tarih_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Giriş Tarihi
        giris_tarihi_label = ctk.CTkLabel(scrollable_frame, text="Giriş Tarihi (GG.AA.YYYY)", text_color=self.colors["text"])
        giris_tarihi_label.pack(anchor="w", padx=20, pady=(0, 5))

        giris_tarihi_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="GG.AA.YYYY")
        giris_tarihi_entry.pack(fill="x", padx=20, pady=(0, 15))
        giris_tarihi_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Notlar
        notlar_label = ctk.CTkLabel(scrollable_frame, text="Notlar:", text_color=self.colors["text"])
        notlar_label.pack(anchor="w", padx=20, pady=(0, 5))

        notlar_entry = ctk.CTkTextbox(scrollable_frame, height=50)
        notlar_entry.pack(fill="x", padx=20, pady=(0, 15))
        notlar_entry.insert("0.0", pasif_sakin.notlar or "")

        # Butonlar
        button_frame = ctk.CTkFrame(modal, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # İptal butonu
        cancel_button = ctk.CTkButton(
            button_frame,
            text="İptal",
            command=modal.destroy,
            fg_color=self.colors["text_secondary"],
            hover_color=self.colors["border"],
            width=100
        )
        cancel_button.pack(side="left", padx=(0, 10))

        # Aktif Yap butonu
        aktif_button = ctk.CTkButton(
            button_frame,
            text="Aktif Yap",
            command=lambda: self.validate_and_confirm_aktif_yap(modal, pasif_sakin.id, ad_entry, rutbe_entry, daire_combo,
                                                            telefon_entry, email_entry, aile_sayisi_entry,
                                                            tahsis_tarih_entry, giris_tarihi_entry, notlar_entry),
            fg_color=self.colors["primary"],
            hover_color=self.colors["text_secondary"],
            width=100
        )
        aktif_button.pack(side="right")

    def validate_and_confirm_aktif_yap(self, modal: Any, pasif_sakin_id: int, ad_entry: Any, rutbe_entry: Any,
                                     daire_combo: Any, telefon_entry: Any, email_entry: Any, aile_sayisi_entry: Any,
                                     tahsis_tarih_entry: Any, giris_tarihi_entry: Any, notlar_entry: Any) -> None:
        """UI validasyonlarını yap ve aktif yapma işlemini onayla"""
        # Ad Soyad
        ad_soyad = ad_entry.get().strip()
        if not ad_soyad:
            show_error(parent=modal, title="Boş Alan", message="Ad Soyad zorunludur!")
            ad_entry.focus()
            return

        # Rütbe/Ünvan
        rutbe = rutbe_entry.get().strip()

        # Telefon
        telefon = telefon_entry.get().strip()

        # E-posta
        email = email_entry.get().strip()

        # Aile Birey Sayısı
        aile_sayisi = aile_sayisi_entry.get().strip()
        if not aile_sayisi:
            show_error(parent=modal, title="Boş Alan", message="Aile Birey Sayısı zorunludur!")
            aile_sayisi_entry.focus()
            return

        try:
            int(aile_sayisi)
        except ValueError:
            show_error(parent=modal, title="Hata", message="Aile Birey Sayısı sayı olmalıdır!")
            aile_sayisi_entry.focus()
            return

        # Tahsis Tarihi
        tahsis_tarih = tahsis_tarih_entry.get().strip()
        if not tahsis_tarih:
            show_error(parent=modal, title="Boş Alan", message="Tahsis Tarihi zorunludur!")
            tahsis_tarih_entry.focus()
            return

        try:
            tahsis_tarihi = datetime.strptime(tahsis_tarih, "%d.%m.%Y")
        except ValueError:
            show_error(parent=modal, title="Hata", message="Tahsis Tarihi GG.AA.YYYY formatında olmalıdır!")
            tahsis_tarih_entry.focus()
            return

        # Giriş Tarihi
        giris_tarihi = giris_tarihi_entry.get().strip()
        if not giris_tarihi:
            show_error(parent=modal, title="Boş Alan", message="Giriş Tarihi zorunludur!")
            giris_tarihi_entry.focus()
            return

        try:
            giris_tarihi_parsed = datetime.strptime(giris_tarihi, "%d.%m.%Y")
        except ValueError:
            show_error(parent=modal, title="Hata", message="Giriş Tarihi GG.AA.YYYY formatında olmalıdır!")
            giris_tarihi_entry.focus()
            return

        # Notlar
        notlar = notlar_entry.get("0.0", "end").strip()

        # Seçilen daireyi al
        selected_daire = daire_combo.get().strip()
        if selected_daire == "Seçiniz...":
            show_error(parent=modal, title="Seçim Yapılmadı", message="Lütfen bir daire seçin!")
            daire_combo.focus()
            return

        # Daireyi bul
        # Format: "Lojman Adı Blok-Numara" (e.g., "İstanbul Lojmanı A-101")
        # Split from the right to handle lojman names with spaces
        parts = selected_daire.rsplit(" ", 1)
        if len(parts) != 2:
            show_error(parent=modal, title="Hata", message="Seçilen daire formatı geçersiz!")
            daire_combo.focus()
            return
            
        blok_daire_part = parts[1]  # "A-101"
        blok_daire_parts = blok_daire_part.split("-", 1)  # Max split=1 for daire numbers like "01-A"
        if len(blok_daire_parts) != 2:
            show_error(parent=modal, title="Hata", message="Seçilen daire formatı geçersiz!")
            daire_combo.focus()
            return
            
        blok_ad = blok_daire_parts[0]  # "A"
        daire_no = blok_daire_parts[1]  # "101"
        blok_lojman_ad = parts[0]  # "İstanbul Lojmanı"
        
        daire = next(
            (d for d in self.daireler if d.blok.lojman.ad == blok_lojman_ad and d.blok.ad == blok_ad and str(d.daire_no) == daire_no),
            None
        )

        if not daire:
            show_error(parent=modal, title="Bulunamadı", message="Seçilen daire bulunamadı!")
            daire_combo.focus()
            return

        # Validasyon başarılı, gerçek işlemi yap
        self.confirm_aktif_yap(modal, pasif_sakin_id, ad_soyad, rutbe, daire.id, telefon, email, aile_sayisi,
                              tahsis_tarihi, giris_tarihi_parsed, notlar)

    def confirm_aktif_yap(self, modal: Any, pasif_sakin_id: int, ad_soyad: str, rutbe: str, daire_id: int, telefon: str,
                         email: str, aile_sayisi: str, tahsis_tarihi: datetime, giris_tarihi: datetime, notlar: str) -> None:
        """
        Pasif sakini yeni aktif sakin olarak ekleme işlemini onayla.
        
        ÖNEMLI: Arşivdeki sakin kaydı silinmez, bunun yerine yeni aktif sakin oluşturulur.
        Bu, giriş/çıkış tarihlerine göre hesap yapılmadığında raporlama karışıklığını önler.
        
        Args:
            modal: Modal window
            pasif_sakin_id: Arşivdeki sakin ID'si (sadece referans için, silme için değil)
            ad_soyad: Yeni aktif sakininin adı soyadı
            rutbe: Rütbe/Ünvan
            daire_id: Daire ID'si
            telefon: Telefon numarası
            email: E-posta adresi
            aile_sayisi: Aile birey sayısı
            tahsis_tarihi: Tahsis tarihi
            giris_tarihi: Giriş tarihi
            notlar: Notlar
        """
        try:
            # Yeni aktif sakin oluştur (eski sakin kaydını silme!)
            new_sakin_data = {
                "ad_soyad": ad_soyad,
                "rutbe_unvan": rutbe,
                "daire_id": daire_id,
                "telefon": telefon,
                "email": email,
                "aile_birey_sayisi": int(aile_sayisi),
                "tahsis_tarihi": tahsis_tarihi,
                "giris_tarihi": giris_tarihi,
                "notlar": notlar,
                "cikis_tarihi": None  # Aktif sakin = çıkış tarihi yok
            }
            
            # Yeni sakin oluştur (create() metodu dict alıyor, kwargs değil)
            new_sakin = self.sakin_controller.create(new_sakin_data)
            show_success("Başarılı", f"Sakin '{ad_soyad}' yeni aktif sakin olarak eklendi!\n"
                                     f"Eski arşiv kaydı korunmuştur (ID: #{pasif_sakin_id})", parent=modal)

        except DuplicateError as e:
            show_error(parent=modal, title="Yinelenen Kayıt", message=str(e.message))
            return
        except ValidationError as e:
            show_error(parent=modal, title="Validasyon Hatası", message=str(e.message))
            return
        except NotFoundError as e:
            show_error(parent=modal, title="Bulunamadı", message=str(e.message))
            return
        except DatabaseError as e:
            show_error(parent=modal, title="Veritabanı Hatası", message=str(e.message))
            return
        except Exception as e:
            handle_exception(e, parent=modal)
            return

        # Modal'ı kapat
        modal.destroy()

        # Listeyi yenile
        self.load_data()

    def open_sakin_modal(self, sakin: Optional[Sakin]) -> None:
        """Sakin düzenleme modal'ını aç"""
        # Modal pencere
        modal = ctk.CTkToplevel(self.frame)
        modal.title("Sakin Ekle/Düzenle")
        modal.geometry("400x500")
        modal.transient(self.frame)
        modal.lift()
        modal.focus_force()

        # Başlık
        title_label = ctk.CTkLabel(
            modal,
            text="Sakin Ekle/Düzenle",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(20, 10))

        # Scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(modal, fg_color=self.colors["surface"])
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Form alanları
        # Ad Soyad
        ad_label = ctk.CTkLabel(scrollable_frame, text="Ad Soyad:", text_color=self.colors["text"])
        ad_label.pack(anchor="w", padx=20, pady=(20, 5))

        ad_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: Ahmet Yılmaz")
        ad_entry.pack(fill="x", padx=20, pady=(0, 15))
        if sakin:
            ad_entry.insert(0, sakin.ad_soyad or "")

        # Rütbe/Ünvan
        rutbe_label = ctk.CTkLabel(scrollable_frame, text="Rütbesi/Ünvanı:", text_color=self.colors["text"])
        rutbe_label.pack(anchor="w", padx=20, pady=(0, 5))

        rutbe_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: Öğretmen")
        rutbe_entry.pack(fill="x", padx=20, pady=(0, 15))
        if sakin:
            rutbe_entry.insert(0, sakin.rutbe_unvan or "")

        # Dairesi (Opsiyonel)
        daire_label = ctk.CTkLabel(scrollable_frame, text="Dairesi:", text_color=self.colors["text"])
        daire_label.pack(anchor="w", padx=20, pady=(0, 5))

        # Daire seçeneklerini hazırla (boş daireler + sakin'in mevcut dairesi)
        daireler_list = self.daire_controller.get_bos_daireler()
        daire_options = ["Seçiniz..."]
        
        # Sakin'in mevcut dairesini listeye ekle (detached instance hatası önlemek için)
        sakin_daire_str = None
        if sakin and sakin.daire:
            sakin_daire_str = f"{sakin.daire.blok.lojman.ad} {sakin.daire.blok.ad}-{sakin.daire.daire_no}"
            if sakin_daire_str not in daire_options:
                daire_options.append(sakin_daire_str)
        
        # Boş daireleri ekle
        for daire in daireler_list:
            daire_str = f"{daire.blok.lojman.ad} {daire.blok.ad}-{daire.daire_no}"
            if daire_str not in daire_options:
                daire_options.append(daire_str)

        daire_combo = ctk.CTkComboBox(scrollable_frame, values=daire_options)
        daire_combo.pack(fill="x", padx=20, pady=(0, 15))
        if sakin_daire_str:
            daire_combo.set(sakin_daire_str)
        else:
            daire_combo.set("Seçiniz...")

        # Telefon
        telefon_label = ctk.CTkLabel(scrollable_frame, text="Telefon:", text_color=self.colors["text"])
        telefon_label.pack(anchor="w", padx=20, pady=(0, 5))

        telefon_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 0532 123 45 67")
        telefon_entry.pack(fill="x", padx=20, pady=(0, 15))
        if sakin:
            telefon_entry.insert(0, sakin.telefon or "")

        # E-posta
        email_label = ctk.CTkLabel(scrollable_frame, text="E-posta:", text_color=self.colors["text"])
        email_label.pack(anchor="w", padx=20, pady=(0, 5))

        email_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: ahmet.yilmaz@example.com")
        email_entry.pack(fill="x", padx=20, pady=(0, 15))
        if sakin:
            email_entry.insert(0, sakin.email or "")

        # Aile Birey Sayısı
        aile_sayisi_label = ctk.CTkLabel(scrollable_frame, text="Aile Birey Sayısı:", text_color=self.colors["text"])
        aile_sayisi_label.pack(anchor="w", padx=20, pady=(0, 5))

        aile_sayisi_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 3")
        aile_sayisi_entry.pack(fill="x", padx=20, pady=(0, 15))
        if sakin:
            aile_sayisi_entry.insert(0, sakin.aile_birey_sayisi or "")

        # Tahsis Tarihi
        tahsis_tarih_label = ctk.CTkLabel(scrollable_frame, text="Tahsis Tarihi (GG.AA.YYYY)", text_color=self.colors["text"])
        tahsis_tarih_label.pack(anchor="w", padx=20, pady=(0, 5))

        tahsis_tarih_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="GG.AA.YYYY")
        tahsis_tarih_entry.pack(fill="x", padx=20, pady=(0, 15))
        if sakin and sakin.tahsis_tarihi:
            tahsis_tarih_entry.insert(0, sakin.tahsis_tarihi.strftime("%d.%m.%Y"))

        # Giriş Tarihi
        giris_tarihi_label = ctk.CTkLabel(scrollable_frame, text="Giriş Tarihi (GG.AA.YYYY)", text_color=self.colors["text"])
        giris_tarihi_label.pack(anchor="w", padx=20, pady=(0, 5))

        giris_tarihi_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="GG.AA.YYYY")
        giris_tarihi_entry.pack(fill="x", padx=20, pady=(0, 15))
        if sakin and sakin.giris_tarihi:
            giris_tarihi_entry.insert(0, sakin.giris_tarihi.strftime("%d.%m.%Y"))

        # Notlar
        notlar_label = ctk.CTkLabel(scrollable_frame, text="Notlar:", text_color=self.colors["text"])
        notlar_label.pack(anchor="w", padx=20, pady=(0, 5))

        notlar_entry = ctk.CTkTextbox(scrollable_frame, height=50)
        notlar_entry.pack(fill="x", padx=20, pady=(0, 15))
        if sakin:
            notlar_entry.insert("0.0", sakin.notlar or "")

        # Butonlar
        button_frame = ctk.CTkFrame(modal, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # İptal butonu
        cancel_button = ctk.CTkButton(
            button_frame,
            text="İptal",
            command=modal.destroy,
            fg_color=self.colors["text_secondary"],
            hover_color=self.colors["border"],
            width=100
        )
        cancel_button.pack(side="left", padx=(0, 10))

        # Kaydet butonu
        save_button = ctk.CTkButton(
            button_frame,
            text="Kaydet",
            command=lambda: self.validate_and_confirm_sakin(modal, sakin, ad_entry, rutbe_entry, daire_combo,
                                                         telefon_entry, email_entry, aile_sayisi_entry,
                                                         tahsis_tarih_entry, giris_tarihi_entry, notlar_entry),
            fg_color=self.colors["primary"],
            hover_color=self.colors["text_secondary"],
            width=100
        )
        save_button.pack(side="right")

    def validate_and_confirm_sakin(self, modal: Any, sakin: Optional[Sakin], ad_entry: Any, rutbe_entry: Any,
                                  daire_combo: Any, telefon_entry: Any, email_entry: Any, aile_sayisi_entry: Any,
                                  tahsis_tarih_entry: Any, giris_tarihi_entry: Any, notlar_entry: Any) -> None:
        """UI validasyonlarını yap ve sakini kaydet"""
        # Ad Soyad
        ad_soyad = ad_entry.get().strip()
        if not ad_soyad:
            show_error(parent=modal, title="Boş Alan", message="Ad Soyad zorunludur!")
            ad_entry.focus()
            return

        # Rütbe/Ünvan
        rutbe = rutbe_entry.get().strip()

        # Telefon
        telefon = telefon_entry.get().strip()

        # E-posta
        email = email_entry.get().strip()

        # Aile Birey Sayısı
        aile_sayisi = aile_sayisi_entry.get().strip()
        if not aile_sayisi:
            show_error(parent=modal, title="Boş Alan", message="Aile Birey Sayısı zorunludur!")
            aile_sayisi_entry.focus()
            return

        try:
            int(aile_sayisi)
        except ValueError:
            show_error(parent=modal, title="Hata", message="Aile Birey Sayısı sayı olmalıdır!")
            aile_sayisi_entry.focus()
            return

        # Tahsis Tarihi
        tahsis_tarih = tahsis_tarih_entry.get().strip()
        if not tahsis_tarih:
            show_error(parent=modal, title="Boş Alan", message="Tahsis Tarihi zorunludur!")
            tahsis_tarih_entry.focus()
            return

        try:
            tahsis_tarihi = datetime.strptime(tahsis_tarih, "%d.%m.%Y")
        except ValueError:
            show_error(parent=modal, title="Hata", message="Tahsis Tarihi GG.AA.YYYY formatında olmalıdır!")
            tahsis_tarih_entry.focus()
            return

        # Giriş Tarihi
        giris_tarihi = giris_tarihi_entry.get().strip()
        if not giris_tarihi:
            show_error(parent=modal, title="Boş Alan", message="Giriş Tarihi zorunludur!")
            giris_tarihi_entry.focus()
            return

        try:
            giris_tarihi_parsed = datetime.strptime(giris_tarihi, "%d.%m.%Y")
        except ValueError:
            show_error(parent=modal, title="Hata", message="Giriş Tarihi GG.AA.YYYY formatında olmalıdır!")
            giris_tarihi_entry.focus()
            return

        # Notlar
        notlar = notlar_entry.get("0.0", "end").strip()

        # Seçilen daireyi al
        selected_daire = daire_combo.get().strip()
        if selected_daire == "Seçiniz...":
            show_error(parent=modal, title="Seçim Yapılmadı", message="Lütfen bir daire seçin!")
            daire_combo.focus()
            return

        # Sakin'in mevcut dairesini kontrol et (düzenleme varsa)
        daire_id = None
        if sakin and sakin.daire:
            sakin_daire_str = f"{sakin.daire.blok.lojman.ad} {sakin.daire.blok.ad}-{sakin.daire.daire_no}"
            if selected_daire == sakin_daire_str:
                # Sakin'in mevcut dairesi seçildi
                daire_id = sakin.daire.id
        
        # Boş daireler listesinde ara
        if not daire_id:
            # Format: "Lojman Adı Blok-Numara" (e.g., "İstanbul Lojmanı A-101")
            # Split from the right to handle lojman names with spaces
            parts = selected_daire.rsplit(" ", 1)
            if len(parts) != 2:
                show_error(parent=modal, title="Hata", message="Seçilen daire formatı geçersiz!")
                daire_combo.focus()
                return
                
            blok_daire_part = parts[1]  # "A-101"
            blok_daire_parts = blok_daire_part.split("-", 1)  # Max split=1 for daire numbers like "01-A"
            if len(blok_daire_parts) != 2:
                show_error(parent=modal, title="Hata", message="Seçilen daire formatı geçersiz!")
                daire_combo.focus()
                return
                
            blok_ad = blok_daire_parts[0]  # "A"
            daire_no = blok_daire_parts[1]  # "101"
            blok_lojman_ad = parts[0]  # "İstanbul Lojmanı"
            
            daire = next(
                (d for d in self.daireler if d.blok.lojman.ad == blok_lojman_ad and d.blok.ad == blok_ad and str(d.daire_no) == daire_no),
                None
            )

            if not daire:
                show_error(parent=modal, title="Bulunamadı", message="Seçilen daire bulunamadı!")
                daire_combo.focus()
                return
            
            daire_id = daire.id

        # Validasyon başarılı, gerçek işlemi yap
        self.confirm_sakin(modal, sakin, ad_soyad, rutbe, daire_id, telefon, email, aile_sayisi,
                          tahsis_tarihi, giris_tarihi_parsed, notlar)

    def confirm_sakin(self, modal: Any, sakin: Optional[Sakin], ad_soyad: str, rutbe: str, daire_id: int, telefon: str,
                     email: str, aile_sayisi: str, tahsis_tarihi: datetime, giris_tarihi: datetime, notlar: str) -> None:
        """Sakini kaydet"""
        try:
            if sakin:
                # Update existing sakin
                update_data = {
                    "ad_soyad": ad_soyad,
                    "rutbe_unvan": rutbe,
                    "daire_id": daire_id,
                    "telefon": telefon,
                    "email": email,
                    "aile_birey_sayisi": int(aile_sayisi),
                    "tahsis_tarihi": tahsis_tarihi,
                    "giris_tarihi": giris_tarihi,
                    "notlar": notlar
                }
                self.sakin_controller.update(sakin.id, update_data)
                show_success(parent=modal, title="Başarılı", message=f"Sakin #{sakin.id} başarıyla güncellendi!")
            else:
                # Create new sakin
                create_data = {
                    "ad_soyad": ad_soyad,
                    "rutbe_unvan": rutbe,
                    "daire_id": daire_id,
                    "telefon": telefon,
                    "email": email,
                    "aile_birey_sayisi": int(aile_sayisi),
                    "tahsis_tarihi": tahsis_tarihi,
                    "giris_tarihi": giris_tarihi,
                    "notlar": notlar
                }
                self.sakin_controller.create(create_data)
                show_success(parent=modal, title="Başarılı", message="Yeni sakin başarıyla eklendi!")

        except DuplicateError as e:
            show_error(parent=modal, title="Yinelenen Kayıt", message=str(e.message))
            return
        except NotFoundError as e:
            show_error(parent=modal, title="Bulunamadı", message=str(e.message))
            return
        except DatabaseError as e:
            show_error(parent=modal, title="Veritabanı Hatası", message=str(e.message))
            return
        except Exception as e:
            handle_exception(e, parent=modal)
            return

        # Modal'ı kapat
        modal.destroy()

        # Listeyi yenile
        self.load_data()

    def setup_aktif_filtre_paneli(self, main_frame: Any) -> None:
        """Aktif sakinler için filtre paneli"""
        # Dış frame
        filter_frame = ctk.CTkFrame(
            main_frame, 
            fg_color=self.colors["background"],
            border_width=2,
            border_color=self.colors["primary"]
        )
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))
        
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
        
        # Ad Soyad filtresi
        ad_soyad_label = ctk.CTkLabel(
            filters_container, 
            text="Ad Soyad:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        ad_soyad_label.pack(side="left", padx=(0, 8))
        
        self.filter_aktif_ad_entry = ctk.CTkEntry(
            filters_container,
            placeholder_text="Örn: Ahmet Yılmaz",
            width=130,
            height=28,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.filter_aktif_ad_entry.pack(side="left", padx=(0, 20))
        self.filter_aktif_ad_entry.bind("<KeyRelease>", self.uygula_aktif_filtreler)
        
        # Daire filtresi
        daire_label = ctk.CTkLabel(
            filters_container,
            text="Daire:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        daire_label.pack(side="left", padx=(0, 8))
        
        self.filter_aktif_daire_combo = ctk.CTkComboBox(
            filters_container,
            values=["Tümü"],
            command=lambda v: self.uygula_aktif_filtreler(),
            width=130,
            height=28,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=10)
        )
        self.filter_aktif_daire_combo.set("Tümü")
        self.filter_aktif_daire_combo.pack(side="left", padx=(0, 20))
        self.filter_aktif_daire_combo.bind("<<ComboboxSelected>>", self.uygula_aktif_filtreler)
        
        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filters_container,
            text="🔄 Temizle",
            command=self.temizle_aktif_filtreler,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=10, weight="bold"),
            height=28,
            width=80,
            corner_radius=4
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def setup_pasif_filtre_paneli(self, main_frame: Any) -> None:
        """Pasif sakinler için filtre paneli"""
        # Dış frame
        filter_frame = ctk.CTkFrame(
            main_frame, 
            fg_color=self.colors["background"],
            border_width=2,
            border_color=self.colors["primary"]
        )
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))
        
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
        
        # Ad Soyad filtresi
        ad_soyad_label = ctk.CTkLabel(
            filters_container, 
            text="Ad Soyad:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        ad_soyad_label.pack(side="left", padx=(0, 8))
        
        self.filter_pasif_ad_entry = ctk.CTkEntry(
            filters_container,
            placeholder_text="Örn: Ahmet Yılmaz",
            width=130,
            height=28,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.filter_pasif_ad_entry.pack(side="left", padx=(0, 20))
        self.filter_pasif_ad_entry.bind("<KeyRelease>", self.uygula_pasif_filtreler)
        
        # Daire filtresi
        daire_label = ctk.CTkLabel(
            filters_container,
            text="Daire:",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10)
        )
        daire_label.pack(side="left", padx=(0, 8))
        
        self.filter_pasif_daire_combo = ctk.CTkComboBox(
            filters_container,
            values=["Tümü"],
            command=lambda v: self.uygula_pasif_filtreler(),
            width=130,
            height=28,
            button_color=self.colors["primary"],
            button_hover_color=self.colors["success"],
            dropdown_font=ctk.CTkFont(size=10)
        )
        self.filter_pasif_daire_combo.set("Tümü")
        self.filter_pasif_daire_combo.pack(side="left", padx=(0, 20))
        self.filter_pasif_daire_combo.bind("<<ComboboxSelected>>", self.uygula_pasif_filtreler)
        
        # Temizle butonu
        temizle_btn = ctk.CTkButton(
            filters_container,
            text="🔄 Temizle",
            command=self.temizle_pasif_filtreler,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            text_color="white",
            font=ctk.CTkFont(size=10, weight="bold"),
            height=28,
            width=80,
            corner_radius=4
        )
        temizle_btn.pack(side="left", padx=(0, 0))

    def uygula_aktif_filtreler(self, event: Optional[Any] = None) -> None:
        """Aktif sakinler için filtreleri uygula"""
        ad_soyad = self.filter_aktif_ad_entry.get().strip().lower()
        daire = self.filter_aktif_daire_combo.get().strip()
        
        # Treeview'i temizle
        for item in self.aktif_sakin_tree.get_children():
            self.aktif_sakin_tree.delete(item)
        
        # Filtre uygula
        for sakin in self.aktif_sakinler:
            # Ad soyad filtresi
            if ad_soyad and ad_soyad not in sakin.ad_soyad.lower():
                continue
                
            # Daire filtresi
            daire_info = ""
            if sakin.daire:
                daire_info = f"{sakin.daire.blok.lojman.ad} {sakin.daire.blok.ad}-{sakin.daire.daire_no}"
            if daire != "Tümü" and daire != daire_info:
                continue
            
            # Filtreden geçen kayıtları ekle
            self.aktif_sakin_tree.insert("", "end", values=(
                sakin.id,
                sakin.ad_soyad,
                sakin.rutbe_unvan or "",
                daire_info,
                sakin.telefon or "",
                sakin.email or "",
                sakin.aile_birey_sayisi,
                sakin.tahsis_tarihi.strftime("%d.%m.%Y") if sakin.tahsis_tarihi else "",
                sakin.giris_tarihi.strftime("%d.%m.%Y") if sakin.giris_tarihi else "",
                sakin.notlar or ""
            ))

    def uygula_pasif_filtreler(self, event: Optional[Any] = None) -> None:
        """Pasif sakinler için filtreleri uygula"""
        ad_soyad = self.filter_pasif_ad_entry.get().strip().lower()
        daire = self.filter_pasif_daire_combo.get().strip()
        
        # Treeview'i temizle
        for item in self.pasif_sakin_tree.get_children():
            self.pasif_sakin_tree.delete(item)
        
        # Filtre uygula
        for sakin in self.pasif_sakinler:
            # Ad soyad filtresi
            if ad_soyad and ad_soyad not in sakin.ad_soyad.lower():
                continue
                
            # Daire filtresi
            daire_info = ""
            if sakin.daire:
                daire_info = f"{sakin.daire.blok.lojman.ad} {sakin.daire.blok.ad}-{sakin.daire.daire_no}"
            elif sakin.eski_daire:
                daire_info = f"{sakin.eski_daire.blok.lojman.ad} {sakin.eski_daire.blok.ad}-{sakin.eski_daire.daire_no}"
            if daire != "Tümü" and daire != daire_info:
                continue
            
            # Filtreden geçen kayıtları ekle
            self.pasif_sakin_tree.insert("", "end", values=(
                sakin.id,
                sakin.ad_soyad,
                sakin.rutbe_unvan or "",
                daire_info,
                sakin.telefon or "",
                sakin.email or "",
                sakin.aile_birey_sayisi,
                sakin.giris_tarihi.strftime("%d.%m.%Y") if sakin.giris_tarihi else "",
                sakin.cikis_tarihi.strftime("%d.%m.%Y") if sakin.cikis_tarihi else ""
            ))

    def temizle_aktif_filtreler(self) -> None:
        """Aktif sakinler için filtreleri temizle"""
        self.filter_aktif_ad_entry.delete(0, "end")
        self.filter_aktif_daire_combo.set("Tümü")
        self.load_aktif_sakinler()

    def temizle_pasif_filtreler(self) -> None:
        """Pasif sakinler için filtreleri temizle"""
        self.filter_pasif_ad_entry.delete(0, "end")
        self.filter_pasif_daire_combo.set("Tümü")
        self.load_pasif_sakinler()
