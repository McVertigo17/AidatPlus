"""
Ayarlar paneli
"""

import customtkinter as ctk
from tkinter import ttk, Menu, filedialog, messagebox
import tkinter as tk
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime
from ui.base_panel import BasePanel
from ui.error_handler import (
    ErrorHandler, handle_exception, show_error, show_success, show_warning,
    UIValidator
)
from controllers.kategori_yonetim_controller import KategoriYonetimController
from controllers.backup_controller import BackupController
from models.base import AnaKategori, AltKategori
from models.exceptions import ValidationError, FileError, ConfigError


class AyarlarPanel(BasePanel):
    """Ayarlar yönetimi paneli
    
    Kategori yönetimi ve yedekleme işlemlerini sağlar.
    İki sekmeden oluşur: Kategori Yönetimi ve Yedekleme
    
    Attributes:
        kategori_controller (KategoriYonetimController): Kategori yönetim denetleyicisi
        backup_controller (BackupController): Yedekleme denetleyicisi
    """

    def __init__(self, parent: ctk.CTk, colors: dict) -> None:
        self.kategori_controller = KategoriYonetimController()
        self.backup_controller = BackupController()
        super().__init__(parent, "⚙️ Ayarlar", colors)

    def setup_ui(self) -> None:
        """UI'yi oluştur"""
        # Ana container
        main_frame = ctk.CTkFrame(self.frame, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab kontrolü
        self.tabview = ctk.CTkTabview(main_frame, width=1000, height=600)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab'ları oluştur
        self.tabview.add("Kategori Yönetimi")
        self.tabview.add("Yedekleme")

        # Tab içeriklerini oluştur
        self.setup_kategori_tab()
        self.setup_yedekleme_tab()

        # Başlangıç verilerini yükle
        try:
            self.load_data()
        except Exception as e:
            # Veritabanı henüz hazır değilse sessizce geç
            pass

    def setup_kategori_tab(self) -> None:
        """Modern kategori yönetimi tab'ı"""
        tab = self.tabview.tab("Kategori Yönetimi")

        # Ana container
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Üst butonlar alanı
        buttons_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"])
        buttons_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Kategori ekle butonu
        self.kategori_ekle_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ Yeni Kategori Ekle",
            command=self.open_kategori_ekle_modal,
            fg_color=self.colors["primary"],
            hover_color=self.colors["success"],
            height=35,
            width=150
        )
        self.kategori_ekle_btn.pack(side="left", padx=(0, 5))

        # Kategori düzenleme ve silme butonları
        self.kategori_duzenle_btn = ctk.CTkButton(
            buttons_frame,
            text="✏️ Düzenle",
            command=self.duzenle_kategori,
            fg_color=self.colors["warning"],
            hover_color=self.colors["error"],
            height=35,
            width=80
        )
        self.kategori_duzenle_btn.pack(side="left", padx=(5, 2))

        self.kategori_sil_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Sil",
            command=self.sil_kategori,
            fg_color=self.colors["error"],
            hover_color=self.colors["warning"],
            height=35,
            width=60
        )
        self.kategori_sil_btn.pack(side="left", padx=(2, 0))

        # Ana içerik alanı
        content_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"])
        content_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Kategori listesi
        self.kategori_tree = ttk.Treeview(
            content_frame,
            columns=("seviye", "gelir_gider", "ana_kategori", "aciklama"),
            show="tree headings",
            height=25
        )
        
        # Sütun başlıklarını ayarla
        self.kategori_tree.heading("#0", text="Kategori Adı")
        self.kategori_tree.heading("seviye", text="Seviye")
        self.kategori_tree.heading("gelir_gider", text="Türü")
        self.kategori_tree.heading("ana_kategori", text="Ana Kategori")
        self.kategori_tree.heading("aciklama", text="Açıklama")
        
        # Sütun genişliklerini ayarla
        self.kategori_tree.column("#0", width=200)
        self.kategori_tree.column("seviye", width=100)
        self.kategori_tree.column("gelir_gider", width=80)
        self.kategori_tree.column("ana_kategori", width=120)
        self.kategori_tree.column("aciklama", width=150)
        
        # Scrollbar ekle (sadece dikey)
        tree_scroll_y = ttk.Scrollbar(content_frame, orient="vertical", command=self.kategori_tree.yview)
        self.kategori_tree.configure(yscrollcommand=tree_scroll_y.set)
        
        # Treeview'i yerleştir
        self.kategori_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        tree_scroll_y.pack(side="right", fill="y", padx=(0, 5), pady=5)

        # Alt bilgi alanı
        info_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["accent"])
        info_frame.pack(fill="x", padx=10, pady=(0, 10))

        info_text = """
        💡 Kullanım Kılavuzu:
        • Kategorileri görmek için genişletmek için çift tıklayın
        • Ana kategoriler altında alt kategoriler listelenir
        • Kategori eklemek/düzenlemek/silmek için butonları kullanın
        • Silme işlemi, kategoride kayıt varsa engellenir
        """

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"],
            justify="left"
        ).pack(pady=10, padx=10)

        # Event binding'ler
        self.kategori_tree.bind("<Double-1>", self.on_kategori_double_click)

    def setup_yedekleme_tab(self) -> None:
        """Yedekleme tab'ı"""
        tab = self.tabview.tab("Yedekleme")

        # Scrollable frame oluştur
        scroll_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color=self.colors["background"],
            label_text="Yedekleme İşlemleri"
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Ana container (scrollable frame içinde)
        main_frame = scroll_frame

        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text="📦 Veri Yedekleme ve Geri Yükleme",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(0, 20))

        # Yedekleme işlemleri
        yedek_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"])
        yedek_frame.pack(fill="x", padx=0, pady=(0, 20))

        yedek_title = ctk.CTkLabel(yedek_frame, text="📤 Yedek Al", font=ctk.CTkFont(size=14, weight="bold"))
        yedek_title.pack(pady=(15, 10), anchor="w", padx=10)

        # Excel yedekleme
        excel_frame = ctk.CTkFrame(yedek_frame, fg_color=self.colors["surface"])
        excel_frame.pack(fill="x", padx=10, pady=(0, 10))

        excel_label = ctk.CTkLabel(excel_frame, text="Excel formatında yedek al:", text_color=self.colors["text"])
        excel_label.pack(side="left", padx=10, pady=10)

        excel_button = ctk.CTkButton(
            excel_frame,
            text="Excel Yedek Al",
            command=lambda: self.yedek_al("excel"),
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"]
        )
        excel_button.pack(side="right", padx=10, pady=10)

        # XML yedekleme
        xml_frame = ctk.CTkFrame(yedek_frame, fg_color=self.colors["surface"])
        xml_frame.pack(fill="x", padx=10, pady=(0, 10))

        xml_label = ctk.CTkLabel(xml_frame, text="XML formatında yedek al:", text_color=self.colors["text"])
        xml_label.pack(side="left", padx=10, pady=10)

        xml_button = ctk.CTkButton(
            xml_frame,
            text="XML Yedek Al",
            command=lambda: self.yedek_al("xml"),
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"]
        )
        xml_button.pack(side="right", padx=10, pady=10)

        # Geri yükleme işlemleri
        yukle_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"])
        yukle_frame.pack(fill="x", padx=0, pady=(0, 20))

        yukle_title = ctk.CTkLabel(yukle_frame, text="📥 Geri Yükle", font=ctk.CTkFont(size=14, weight="bold"))
        yukle_title.pack(pady=(15, 10), anchor="w", padx=10)

        # Excel geri yükleme
        excel_yukle_frame = ctk.CTkFrame(yukle_frame, fg_color=self.colors["surface"])
        excel_yukle_frame.pack(fill="x", padx=10, pady=(0, 10))

        excel_yukle_label = ctk.CTkLabel(excel_yukle_frame, text="Excel dosyasından geri yükle:", text_color=self.colors["text"])
        excel_yukle_label.pack(side="left", padx=10, pady=10)

        excel_yukle_button = ctk.CTkButton(
            excel_yukle_frame,
            text="Excel'den Yükle",
            command=lambda: self.yedekten_yukle("excel"),
            fg_color=self.colors["warning"],
            hover_color=self.colors["error"]
        )
        excel_yukle_button.pack(side="right", padx=10, pady=10)

        # XML geri yükleme
        xml_yukle_frame = ctk.CTkFrame(yukle_frame, fg_color=self.colors["surface"])
        xml_yukle_frame.pack(fill="x", padx=10, pady=(0, 10))

        xml_yukle_label = ctk.CTkLabel(xml_yukle_frame, text="XML dosyasından geri yükle:", text_color=self.colors["text"])
        xml_yukle_label.pack(side="left", padx=10, pady=10)

        xml_yukle_button = ctk.CTkButton(
            xml_yukle_frame,
            text="XML'den Yükle",
            command=lambda: self.yedekten_yukle("xml"),
            fg_color=self.colors["warning"],
            hover_color=self.colors["error"]
        )
        xml_yukle_button.pack(side="right", padx=10, pady=10)

        # Uyarı metni
        warning_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["accent"])
        warning_frame.pack(fill="x", padx=0, pady=(20, 10))
        
        warning_label = ctk.CTkLabel(
            warning_frame,
            text="⚠️ UYARI: Geri yükleme işlemi mevcut verilerin üzerine yazacaktır.\nİşlem geri alınamaz, lütfen önceden yedek alın!",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=11, weight="bold"),
            justify="left"
        )
        warning_label.pack(pady=10, padx=10)
        
        # Bilgi metni
        info_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["accent"])
        info_frame.pack(fill="x", padx=0, pady=(0, 20))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="💡 TİP: Excel ve XML formatlarında tam veri yedekleme yapabilirsiniz.\nYedek dosyalarını güvenli bir yerde saklayın.",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=10),
            justify="left"
        )
        info_label.pack(pady=8, padx=10)
        
        # Sıfırlama bölümü
        sifirla_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"])
        sifirla_frame.pack(fill="x", padx=0, pady=(0, 10))
        sifirla_title = ctk.CTkLabel(sifirla_frame, text="⚡ Veritabanını Sıfırla", font=ctk.CTkFont(size=14, weight="bold"))
        sifirla_title.pack(pady=(15, 10), anchor="w", padx=10)

        # Sıfırlama açıklaması
        sifirla_desc_frame = ctk.CTkFrame(sifirla_frame, fg_color=self.colors["surface"])
        sifirla_desc_frame.pack(fill="x", padx=10, pady=(0, 10))

        sifirla_desc = ctk.CTkLabel(
            sifirla_desc_frame,
            text="Veritabanındaki TÜM verileri siler ve uygulamayı sıfırdan başlamaya hazır hale getirir.",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=10),
            justify="left"
        )
        sifirla_desc.pack(anchor="w", pady=5)

        # Sıfırlama butonu
        sifirla_button = ctk.CTkButton(
            sifirla_frame,
            text="🔄 Veritabanını Sıfırla",
            command=self.sifirla_veritabani,
            fg_color=self.colors["error"],
            hover_color=self.colors["warning"],
            height=35
        )
        sifirla_button.pack(side="left", padx=10, pady=(0, 10))

        # Sıfırlama uyarısı
        sifirla_warning = ctk.CTkLabel(
            sifirla_frame,
            text="⚠️ Bu işlem geri alınamaz! Önce yedek alın!",
            text_color=self.colors["error"],
            font=ctk.CTkFont(size=9, weight="bold")
        )
        sifirla_warning.pack(side="left", padx=10, pady=(0, 10))

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_kategori_listesi()

    def load_kategori_listesi(self) -> None:
        """Kategori listesini yükle"""
        # Önceki verileri temizle
        for item in self.kategori_tree.get_children():
            self.kategori_tree.delete(item)

        # Ana kategorileri yükle
        ana_kategoriler = self.kategori_controller.get_ana_kategoriler()
        
        for ana_kategori in ana_kategoriler:
            # Gelir/Gider gösterimini hazırla
            gelir_gider = "💰 Gelir" if ana_kategori.tip == "gelir" else "💸 Gider"
            
            # Ana kategori düğümünü ekle
            ana_node = self.kategori_tree.insert(
                "", "end", 
                iid=f"ana_{ana_kategori.id}",
                text=ana_kategori.name,
                values=("Ana Kategori", gelir_gider, "", ana_kategori.aciklama or "")
            )
            
            # Alt kategorileri yükle
            alt_kategoriler = self.kategori_controller.get_alt_kategoriler_by_parent(ana_kategori.id)
            for alt_kategori in alt_kategoriler:
                self.kategori_tree.insert(
                    ana_node, "end",
                    iid=f"alt_{alt_kategori.id}",
                    text=alt_kategori.name,
                    values=("Alt Kategori", gelir_gider, ana_kategori.name, alt_kategori.aciklama or "")
                )

    # Event handlers
    def on_kategori_double_click(self, event: tk.Event) -> None:
        """Kategoriye çift tıklandığında"""
        item = self.kategori_tree.selection()
        if item:
            # Seçili öğeyi al
            item_id = item[0]
            # Düzenleme işlemi için modal aç
            self.duzenle_kategori()

    # Kategori işlemleri
    def open_kategori_ekle_modal(self) -> None:
        """Yeni kategori ekleme modal'ı"""
        self.open_kategori_modal()

    def open_kategori_modal(self, kategori_data: Optional[dict] = None) -> None:
        """Kategori ekleme/düzenleme modal'ı"""
        modal = ctk.CTkToplevel(self.frame)
        modal.title("Yeni Kategori Ekle" if kategori_data is None else "Kategori Düzenle")
        modal.resizable(False, False)
        
        # Sabit konumlandırma (ekran ortasında)
        modal.geometry("450x500+475+175")
        modal.transient(self.parent)
        modal.lift()
        modal.focus_force()

        # Başlık
        title_label = ctk.CTkLabel(
            modal,
            text="Yeni Kategori Ekle" if kategori_data is None else "Kategori Düzenle",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(20, 15))

        # Gelir/Gider Seçimi (yalnızca ana kategori için)
        gelir_gider_frame = ctk.CTkFrame(modal, fg_color=self.colors["background"])
        gelir_gider_frame.pack(fill="x", padx=20, pady=(0, 10))

        gelir_gider_label = ctk.CTkLabel(gelir_gider_frame, text="Kategori Türü:", text_color=self.colors["text"])
        gelir_gider_label.pack(anchor="w", pady=(0, 5))

        self.gelir_gider_var = tk.StringVar(value=kategori_data.get("gelir_gider", "gelir") if kategori_data else "gelir")
        gelir_gider_inner = ctk.CTkFrame(gelir_gider_frame, fg_color=self.colors["background"])
        gelir_gider_inner.pack(fill="x")

        gelir_radio = ctk.CTkRadioButton(
            gelir_gider_inner,
            text="💰 Gelir",
            variable=self.gelir_gider_var,
            value="gelir"
        )
        gelir_radio.pack(side="left", padx=(0, 20))

        gider_radio = ctk.CTkRadioButton(
            gelir_gider_inner,
            text="💸 Gider",
            variable=self.gelir_gider_var,
            value="gider"
        )
        gider_radio.pack(side="left")

        # Kategori tipi seçimi (Ana/Alt)
        tip_frame = ctk.CTkFrame(modal, fg_color=self.colors["background"])
        tip_frame.pack(fill="x", padx=20, pady=(0, 10))

        tip_label = ctk.CTkLabel(tip_frame, text="Kategori Düzeyi:", text_color=self.colors["text"])
        tip_label.pack(anchor="w", pady=(0, 5))

        self.kategori_tip_var = tk.StringVar(value="ana" if kategori_data is None or kategori_data.get("tip") == "ana" else "alt")
        tip_frame_inner = ctk.CTkFrame(tip_frame, fg_color=self.colors["background"])
        tip_frame_inner.pack(fill="x")

        ana_radio = ctk.CTkRadioButton(
            tip_frame_inner,
            text="Ana Kategori",
            variable=self.kategori_tip_var,
            value="ana",
            command=lambda: self.on_kategori_tip_changed(modal)
        )
        ana_radio.pack(side="left", padx=(0, 20))

        alt_radio = ctk.CTkRadioButton(
            tip_frame_inner,
            text="Alt Kategori",
            variable=self.kategori_tip_var,
            value="alt",
            command=lambda: self.on_kategori_tip_changed(modal)
        )
        alt_radio.pack(side="left")

        # Ana kategori seçimi (sadece alt kategori için)
        self.ana_kategori_frame = ctk.CTkFrame(modal, fg_color=self.colors["background"])
        self.ana_kategori_frame.pack(fill="x", padx=20, pady=(0, 10))

        ana_kategori_label = ctk.CTkLabel(self.ana_kategori_frame, text="Ana Kategori:", text_color=self.colors["text"])
        ana_kategori_label.pack(anchor="w", pady=(0, 5))

        # Ana kategori combobox
        self.ana_kategori_combo = ctk.CTkComboBox(self.ana_kategori_frame, width=300)
        self.ana_kategori_combo.pack(anchor="w")

        # Ana kategori verilerini yükle
        self.load_ana_kategori_combo()

        # Kategori adı
        ad_frame = ctk.CTkFrame(modal, fg_color=self.colors["background"])
        ad_frame.pack(fill="x", padx=20, pady=(0, 10))

        ad_label = ctk.CTkLabel(ad_frame, text="Kategori Adı:", text_color=self.colors["text"])
        ad_label.pack(anchor="w", pady=(0, 5))

        self.ad_entry = ctk.CTkEntry(ad_frame, placeholder_text="Kategori adını girin", width=300)
        self.ad_entry.pack(anchor="w")

        # Açıklama
        aciklama_frame = ctk.CTkFrame(modal, fg_color=self.colors["background"])
        aciklama_frame.pack(fill="x", padx=20, pady=(0, 10))

        aciklama_label = ctk.CTkLabel(aciklama_frame, text="Açıklama (opsiyonel):", text_color=self.colors["text"])
        aciklama_label.pack(anchor="w", pady=(0, 5))

        self.aciklama_entry = ctk.CTkEntry(aciklama_frame, placeholder_text="Açıklama girin (opsiyonel)", width=300)
        self.aciklama_entry.pack(anchor="w")

        # Verileri doldur (düzenleme modu için)
        if kategori_data:
            self.kategori_tip_var.set(kategori_data.get("tip", "ana"))
            self.ad_entry.insert(0, kategori_data.get("name", ""))
            self.aciklama_entry.insert(0, kategori_data.get("aciklama", ""))
            
            if kategori_data.get("tip") == "alt":
                # Ana kategori seçimini ayarla
                parent_name = kategori_data.get("parent_name")
                if parent_name:
                    # Combobox'ta doğru değeri seç
                    values = [self.ana_kategori_combo.cget("values")[i] for i in range(len(self.ana_kategori_combo.cget("values") or []))]
                    for i, value in enumerate(values):
                        if value.startswith(f"{parent_name} (ID:"):
                            self.ana_kategori_combo.set(value)
                            break

        # Başlangıç durumunu ayarla
        self.on_kategori_tip_changed(modal)

        # Butonlar
        button_frame = ctk.CTkFrame(modal, fg_color=self.colors["background"])
        button_frame.pack(fill="x", padx=20, pady=(10, 20))

        cancel_button = ctk.CTkButton(
            button_frame,
            text="İptal",
            command=modal.destroy,
            fg_color=self.colors["text_secondary"],
            hover_color=self.colors["border"]
        )
        cancel_button.pack(side="left", padx=(0, 10))

        save_button = ctk.CTkButton(
            button_frame,
            text="Kaydet",
            command=lambda: self.save_kategori(modal, kategori_data),
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"]
        )
        save_button.pack(side="right")

    def on_kategori_tip_changed(self, modal: ctk.CTkToplevel) -> None:
        """Kategori tipi değiştiğinde"""
        tip = self.kategori_tip_var.get()
        if tip == "ana":
            # Ana kategori seçimi gizle
            self.ana_kategori_frame.pack_forget()
        else:
            # Ana kategori seçimi göster
            self.ana_kategori_frame.pack(fill="x", padx=20, pady=(0, 10))

    def load_ana_kategori_combo(self) -> None:
        """Ana kategori combobox'ını doldur"""
        ana_kategoriler = self.kategori_controller.get_ana_kategoriler()
        values = [f"{kategori.name} (ID: {kategori.id})" for kategori in ana_kategoriler]
        self.ana_kategori_combo.configure(values=values)
        if values:
            self.ana_kategori_combo.set(values[0])

    def save_kategori(self, modal: ctk.CTkToplevel, existing_kategori: Optional[dict]) -> None:
        """Kategoriyi kaydet"""
        # Form validasyonu
        name = UIValidator.validate_text_entry(self.ad_entry, "Kategori Adı", 1, 100)
        if name is None:
            return

        aciklama = self.aciklama_entry.get().strip() or None
        tip = self.kategori_tip_var.get()
        gelir_gider = self.gelir_gider_var.get()

        try:
            if tip == "ana":
                # Ana kategori ekle/güncelle
                with ErrorHandler(parent=modal, show_success_msg=False):
                    if existing_kategori and existing_kategori.get("tip") == "ana":
                        # Güncelleme
                        success = self.kategori_controller.update_ana_kategori(
                            existing_kategori["id"], name, aciklama, gelir_gider
                        )
                        action = "güncellendi"
                    else:
                        # Yeni ekleme
                        kategori = self.kategori_controller.create_ana_kategori(name, aciklama, gelir_gider)
                        success = kategori is not None
                        action = "eklendi"

                    if success:
                        kategori_turu = "Gelir" if gelir_gider == "gelir" else "Gider"
                        msg = f"Ana kategori '{name}' ({kategori_turu}) başarıyla {action}!"
                        modal.destroy()
                        show_success(parent=self.parent, title="Başarılı", message=msg)
                        self.load_data()
                    else:
                        if action == "eklendi":
                            show_error(parent=modal, title="Hata", message="Bu isimde bir ana kategori zaten mevcut!")
                        else:
                            show_error(parent=modal, title="Hata", message="Kategori güncellenirken hata oluştu!")
            else:
                # Alt kategori ekle/güncelle
                selected_ana = self.ana_kategori_combo.get()
                if not selected_ana:
                    show_error(parent=modal, title="Hata", message="Lütfen bir ana kategori seçin!")
                    return

                # ID'yi seçilen metinden çıkar
                try:
                    parent_id = int(selected_ana.split("(ID: ")[1].split(")")[0])
                except (IndexError, ValueError):
                    show_error(parent=modal, title="Hata", message="Geçersiz ana kategori seçimi!")
                    return

                with ErrorHandler(parent=modal, show_success_msg=False):
                    if existing_kategori and existing_kategori.get("tip") == "alt":
                        # Güncelleme
                        success = self.kategori_controller.update_alt_kategori(
                            existing_kategori["id"], name, aciklama, parent_id
                        )
                        action = "güncellendi"
                    else:
                        # Yeni ekleme
                        kategori = self.kategori_controller.create_alt_kategori(parent_id, name, aciklama)
                        success = kategori is not None
                        action = "eklendi"

                    if success:
                        msg = f"Alt kategori '{name}' başarıyla {action}!"
                        modal.destroy()
                        show_success(parent=self.parent, title="Başarılı", message=msg)
                        self.load_data()
                    else:
                        if action == "eklendi":
                            show_error(parent=modal, title="Hata", message="Bu isimde bir alt kategori zaten mevcut!")
                        else:
                            show_error(parent=modal, title="Hata", message="Kategori güncellenirken hata oluştu!")

        except (ValidationError, ConfigError) as e:
            handle_exception(e, parent=modal)
        except Exception as e:
            handle_exception(e, parent=modal)

    def duzenle_kategori(self) -> None:
        """Seçili kategoriyi düzenle"""
        selection = self.kategori_tree.selection()
        if not selection:
            self.show_error("Lütfen düzenlenecek kategoriyi seçin!")
            return

        item_id = selection[0]
        item_values = self.kategori_tree.item(item_id)
        
        # Kategori verilerini hazırla
        is_ana = item_id.startswith("ana_")
        kategori_data = {
            "id": int(item_id.split("_")[1]),  # ID'yi çıkar
            "tip": "ana" if is_ana else "alt",
            "name": item_values["text"],
            "gelir_gider": "gelir" if "Gelir" in item_values["values"][1] else "gider",
            "aciklama": item_values["values"][3] if len(item_values["values"]) > 3 else ""
        }
        
        # Alt kategori ise ana kategori bilgisini de al
        if kategori_data["tip"] == "alt":
            parent_item = self.kategori_tree.parent(item_id)
            if parent_item:
                parent_values = self.kategori_tree.item(parent_item)
                kategori_data["parent_name"] = parent_values["text"]

        self.open_kategori_modal(kategori_data)

    def sil_kategori(self) -> None:
        """Seçili kategoriyi sil"""
        selection = self.kategori_tree.selection()
        if not selection:
            self.show_error("Lütfen silinecek kategoriyi seçin!")
            return

        item_id = selection[0]
        item_values = self.kategori_tree.item(item_id)
        name = item_values["text"]
        tip = "ana" if item_id.startswith("ana_") else "alt"

        # Onay al
        if not self.ask_yes_no(f"'{name}' kategorisi gerçekten silinsin mi?"):
            return

        try:
            success = False
            if tip == "ana":
                # Ana kategori silme
                kategori_id = int(item_id.split("_")[1])
                success = self.kategori_controller.delete_ana_kategori(kategori_id)
                
                if not success:
                    # Alt kategorisi olduğu için silinememiş olabilir
                    self.show_error("Bu ana kategoriye bağlı alt kategoriler var. Önce alt kategorileri silmelisiniz!")
            else:
                # Alt kategori silme
                kategori_id = int(item_id.split("_")[1])
                success = self.kategori_controller.delete_alt_kategori(kategori_id)
                
                if not success:
                    # Finansal işlemlerde kullanıldığı için silinememiş olabilir
                    self.show_error("Bu kategori finansal işlemlerde kullanıldığı için silinemez!")

            if success:
                self.show_message(f"Kategori '{name}' başarıyla silindi!")
                self.load_data()
            elif not success:
                # Hata mesajı zaten gösterildi
                pass

        except Exception as e:
            self.show_error(f"Kategori silinirken hata oluştu: {str(e)}")

    # Yedekleme işlemleri
    def yedek_al(self, format_type: str) -> None:
        """Veritabanını yedekle"""
        try:
            # Yedek dosya adı oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if format_type == "excel":
                filename = f"aidat_plus_yedek_{timestamp}.xlsx"
                filetypes = [("Excel files", "*.xlsx")]
            else:  # xml
                filename = f"aidat_plus_yedek_{timestamp}.xml"
                filetypes = [("XML files", "*.xml")]

            # Dosya kaydetme dialog'u
            filepath = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=filetypes,
                initialfile=filename,
                title=f"Yedek Dosyası Olarak Kaydet ({format_type.upper()})"
            )

            if not filepath:
                return

            # Yedekleme işlemi
            success = False
            if format_type == "excel":
                success = self.backup_controller.backup_to_excel(filepath)
            else:  # xml
                success = self.backup_controller.backup_to_xml(filepath)

            if success:
                file_size = os.path.getsize(filepath) / 1024  # KB cinsinden
                self.show_message(f"✓ Yedek başarıyla alındı!\n\nDosya: {os.path.basename(filepath)}\nBoyut: {file_size:.2f} KB")
            else:
                self.show_error(f"Yedek alma işlemi başarısız oldu!")

        except Exception as e:
            self.show_error(f"Yedek alma işlemi başarısız: {str(e)}")

    def yedekten_yukle(self, format_type: str) -> None:
        """Yedekten geri yükle"""
        try:
            # Dosya seçme dialog'u
            if format_type == "excel":
                filetypes = [("Excel files", "*.xlsx")]
            else:  # xml
                filetypes = [("XML files", "*.xml")]

            filepath = filedialog.askopenfilename(
                filetypes=filetypes,
                title=f"Yedek Dosyası Seç ({format_type.upper()})"
            )

            if not filepath:
                return

            # Dosya kontrolü
            if not os.path.exists(filepath):
                self.show_error("Seçilen dosya bulunamadı!")
                return

            # Onay al
            file_info = f"Dosya: {os.path.basename(filepath)}\nBoyut: {os.path.getsize(filepath) / 1024:.2f} KB"
            if not self.ask_yes_no(f"⚠️ Mevcut veriler silinecek ve yedekten geri yüklenecektir.\n\n{file_info}\n\nDevam edilsin mi?"):
                return

            # Geri yükleme işlemi
            success = False
            error_msg = None
            
            try:
                if format_type == "excel":
                    success = self.backup_controller.restore_from_excel(filepath)
                else:  # xml
                    success = self.backup_controller.restore_from_xml(filepath)
            except Exception as restore_error:
                error_msg = str(restore_error)

            if success:
                self.show_message(f"Yedekten basarili sekilde geri yüklendi!\n\nDosya: {os.path.basename(filepath)}\n\nUygulamayi yeniden baslatabilirsiniz.")
            else:
                if error_msg:
                    self.show_error(f"Geri yükleme işlemi başarısız oldu!\n\nHata: {error_msg}\n\nKonsol çiktisini kontrol edin.")
                else:
                    self.show_error(f"Geri yükleme işlemi başarısız oldu!")

        except Exception as e:
            self.show_error(f"Geri yükleme işlemi başarısız: {str(e)}")

    def sifirla_veritabani(self) -> None:
        """Veritabanını sıfırla - tüm verileri sil"""
        try:
            # İlk uyarı
            if not self.ask_yes_no(
                "⚠️ UYARI: Veritabanındaki TÜM veriler silinecektir!\n\n"
                "Bu işlem geri alınamaz. Devam etmek istediğinizden emin misiniz?",
                title="Sıfırlama Onayı"
            ):
                return
            
            # İkinci onay (çok önemli)
            if not self.ask_yes_no(
                "🔴 SON ONAY: Gerçekten tüm verileri silmek istediğinizi onaylıyor musunuz?\n\n"
                "Bunu geri alamazsınız! Lütfen önceden yedek aldığınızdan emin olun.",
                title="Son Onay - İşlem Geri Alınamaz"
            ):
                return
            
            # Veritabanını sıfırla
            success = self.backup_controller.reset_database()
            
            if success:
                self.show_message(
                    "✓ Veritabanı başarıyla sıfırlandı!\n\n"
                    "Tüm veriler silinmiştir. Uygulamayı yeniden başlatabilirsiniz.",
                    title="Sıfırlama Tamamlandı"
                )
            else:
                self.show_error(
                    "Veritabanı sıfırlama işlemi başarısız oldu!",
                    title="Sıfırlama Hatası"
                )
        
        except Exception as e:
            self.show_error(f"Sıfırlama işlemi başarısız: {str(e)}")