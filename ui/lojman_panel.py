"""
Lojman paneli
"""

import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from typing import List, Optional
from ui.base_panel import BasePanel
from ui.error_handler import (
    ErrorHandler, handle_exception, show_error, show_success, show_warning,
    UIValidator
)
from controllers.lojman_controller import LojmanController
from controllers.blok_controller import BlokController
from controllers.daire_controller import DaireController
from models.base import Lojman, Blok, Daire
from models.exceptions import (
    ValidationError, DatabaseError, NotFoundError, DuplicateError
)


class LojmanPanel(BasePanel):
    """Lojman yönetimi paneli
    
    Lojman komplekslerinin (blok ve daire) yönetimini sağlar.
    Hiyerarşik yapıda: Lojman → Blok → Daire
    
    Attributes:
        lojman_controller (LojmanController): Lojman yönetim denetleyicisi
        blok_controller (BlokController): Blok yönetim denetleyicisi
        daire_controller (DaireController): Daire yönetim denetleyicisi
        lojmanlar (List[Lojman]): Lojman nesneleri listesi
        bloklar (List[Blok]): Blok nesneleri listesi
        daireler (List[Daire]): Daire nesneleri listesi
    """

    def __init__(self, parent: ctk.CTk, colors: dict) -> None:
        self.lojman_controller = LojmanController()
        self.blok_controller = BlokController()
        self.daire_controller = DaireController()

        # Veri saklama
        self.lojmanlar: List[Lojman] = []
        self.bloklar: List[Blok] = []
        self.daireler: List[Daire] = []

        super().__init__(parent, "🏠 Lojman Yönetimi", colors)

    def setup_ui(self) -> None:
        """UI'yi oluştur"""
        # Tab kontrolü
        self.tabview = ctk.CTkTabview(self.frame, width=900, height=600)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Tab'ları oluştur
        self.tabview.add("Lojman Bilgileri")
        self.tabview.add("Blok Bilgileri")
        self.tabview.add("Daire Bilgileri")

        # Tab içeriklerini oluştur
        self.setup_lojman_bilgileri_tab()
        self.setup_blok_tab()
        self.setup_daire_tab()

        # Başlangıç verilerini yükle
        self.load_data()

    def setup_lojman_bilgileri_tab(self) -> None:
        """Lojman bilgileri tab'ı"""
        tab = self.tabview.tab("Lojman Bilgileri")

        # Ana frame
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Sol taraf - Tanımlı lojmanlar
        left_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=0)

        # Başlık
        title_label = ctk.CTkLabel(
            left_frame,
            text="Tanımlı Lojmanlar",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(10, 5))

        # Lojman listesi
        self.lojman_tree = ttk.Treeview(
            left_frame,
            columns=("id", "ad", "adres", "blok_sayisi", "daire_sayisi", "kiraya_esas", "isitilan"),
            show="headings",
            height=15
        )

        # Kolon başlıkları
        self.lojman_tree.heading("id", text="ID")
        self.lojman_tree.heading("ad", text="Lojman Adı")
        self.lojman_tree.heading("adres", text="Adres")
        self.lojman_tree.heading("blok_sayisi", text="Blok Sayısı")
        self.lojman_tree.heading("daire_sayisi", text="Daire Sayısı")
        self.lojman_tree.heading("kiraya_esas", text="Kiraya Esas (m²)")
        self.lojman_tree.heading("isitilan", text="Isıtılan (m²)")

        # Kolon genişlikleri ve ortalaması
        self.lojman_tree.column("id", width=50, anchor="center")
        self.lojman_tree.column("ad", width=150, anchor="center")
        self.lojman_tree.column("adres", width=200, anchor="center")
        self.lojman_tree.column("blok_sayisi", width=80, anchor="center")
        self.lojman_tree.column("daire_sayisi", width=80, anchor="center")
        self.lojman_tree.column("kiraya_esas", width=100, anchor="center")
        self.lojman_tree.column("isitilan", width=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.lojman_tree.yview)
        self.lojman_tree.configure(yscrollcommand=scrollbar.set)

        self.lojman_tree.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))
        scrollbar.pack(side="right", fill="y", pady=(0, 10))

        # Sağ tık menüsü
        self.lojman_context_menu = tk.Menu(self.lojman_tree, tearoff=0)
        self.lojman_context_menu.add_command(label="Düzenle", command=self.edit_lojman)
        self.lojman_context_menu.add_command(label="Sil", command=self.delete_lojman)
        self.lojman_tree.bind("<Button-3>", self.show_lojman_context_menu)

        # Sağ taraf - Yeni lojman ekleme
        right_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=0)

        # Başlık
        add_title = ctk.CTkLabel(
            right_frame,
            text="Yeni Lojman Ekle",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        add_title.pack(pady=(10, 15))

        # Form
        form_frame = ctk.CTkFrame(right_frame, fg_color=self.colors["surface"])
        form_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Lojman adı
        name_label = ctk.CTkLabel(form_frame, text="Lojman Adı:", text_color=self.colors["text"])
        name_label.pack(anchor="w", padx=20, pady=(20, 5))

        self.lojman_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Örn: Ana Lojman")
        self.lojman_name_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Adres
        adres_label = ctk.CTkLabel(form_frame, text="Adres:", text_color=self.colors["text"])
        adres_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.lojman_adres_textbox = ctk.CTkTextbox(form_frame, height=80)
        self.lojman_adres_textbox.pack(fill="x", padx=20, pady=(0, 20))

        # Ekle butonu
        add_button = ctk.CTkButton(
            form_frame,
            text="Lojman Ekle",
            command=self.add_lojman,
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"],
            height=40
        )
        add_button.pack(pady=(0, 20))

    def setup_blok_tab(self) -> None:
        """Blok bilgileri tab'ı"""
        tab = self.tabview.tab("Blok Bilgileri")

        # Ana frame
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Sol taraf - Tanımlı bloklar
        left_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=0)

        # Başlık
        title_label = ctk.CTkLabel(
            left_frame,
            text="Tanımlı Bloklar",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(10, 5))

        # Blok listesi
        self.blok_tree = ttk.Treeview(
            left_frame,
            columns=("id", "lojman", "ad", "kat_sayisi", "giris_kapi", "daire_sayisi", "kiraya_esas", "isitilan", "notlar"),
            show="headings",
            height=15
        )

        # Kolon başlıkları
        self.blok_tree.heading("id", text="ID")
        self.blok_tree.heading("lojman", text="Lojman")
        self.blok_tree.heading("ad", text="Blok")
        self.blok_tree.heading("kat_sayisi", text="Kat Sayısı")
        self.blok_tree.heading("giris_kapi", text="Giriş Kapı")
        self.blok_tree.heading("daire_sayisi", text="Daire Sayısı")
        self.blok_tree.heading("kiraya_esas", text="Kiraya Esas (m²)")
        self.blok_tree.heading("isitilan", text="Isıtılan (m²)")
        self.blok_tree.heading("notlar", text="Notlar")

        # Kolon genişlikleri ve ortalaması
        self.blok_tree.column("id", width=50, anchor="center")
        self.blok_tree.column("lojman", width=120, anchor="center")
        self.blok_tree.column("ad", width=60, anchor="center")
        self.blok_tree.column("kat_sayisi", width=80, anchor="center")
        self.blok_tree.column("giris_kapi", width=80, anchor="center")
        self.blok_tree.column("daire_sayisi", width=80, anchor="center")
        self.blok_tree.column("kiraya_esas", width=100, anchor="center")
        self.blok_tree.column("isitilan", width=100, anchor="center")
        self.blok_tree.column("notlar", width=150, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.blok_tree.yview)
        self.blok_tree.configure(yscrollcommand=scrollbar.set)

        self.blok_tree.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))
        scrollbar.pack(side="right", fill="y", pady=(0, 10))

        # Sağ tık menüsü
        self.blok_context_menu = tk.Menu(self.blok_tree, tearoff=0)
        self.blok_context_menu.add_command(label="Düzenle", command=self.edit_blok)
        self.blok_context_menu.add_command(label="Sil", command=self.delete_blok)
        self.blok_tree.bind("<Button-3>", self.show_blok_context_menu)

        # Sağ taraf - Yeni blok ekleme
        right_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=0)

        # Başlık
        add_title = ctk.CTkLabel(
            right_frame,
            text="Yeni Blok Ekle",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        add_title.pack(pady=(10, 15))

        # Form - Scrollable frame kullanacağız
        scrollable_frame = ctk.CTkScrollableFrame(right_frame, fg_color=self.colors["surface"])
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Bağlı lojman
        lojman_label = ctk.CTkLabel(scrollable_frame, text="Bağlı Lojman:", text_color=self.colors["text"])
        lojman_label.pack(anchor="w", padx=20, pady=(20, 5))

        self.blok_lojman_combo = ctk.CTkComboBox(scrollable_frame, values=[])
        self.blok_lojman_combo.pack(fill="x", padx=20, pady=(0, 15))
        self.blok_lojman_combo.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.blok_lojman_combo))

        # Blok adı
        ad_label = ctk.CTkLabel(scrollable_frame, text="Blok Adı:", text_color=self.colors["text"])
        ad_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.blok_ad_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: A")
        self.blok_ad_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.blok_ad_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.blok_ad_entry))

        # Kat sayısı
        kat_label = ctk.CTkLabel(scrollable_frame, text="Kat Sayısı:", text_color=self.colors["text"])
        kat_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.blok_kat_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 5")
        self.blok_kat_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.blok_kat_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.blok_kat_entry))

        # Giriş kapı no
        giris_label = ctk.CTkLabel(scrollable_frame, text="Giriş Kapı No:", text_color=self.colors["text"])
        giris_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.blok_giris_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 1")
        self.blok_giris_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.blok_giris_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.blok_giris_entry))

        # Notlar
        not_label = ctk.CTkLabel(scrollable_frame, text="Notlar (Opsiyonel):", text_color=self.colors["text"])
        not_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.blok_not_textbox = ctk.CTkTextbox(scrollable_frame, height=60)
        self.blok_not_textbox.pack(fill="x", padx=20, pady=(0, 20))
        self.blok_not_textbox.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.blok_not_textbox))

        # Ekle butonu
        add_button = ctk.CTkButton(
            scrollable_frame,
            text="Blok Ekle",
            command=self.add_blok,
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"],
            height=40
        )
        add_button.pack(pady=(0, 20))

    def setup_daire_tab(self) -> None:
        """Daire bilgileri tab'ı"""
        tab = self.tabview.tab("Daire Bilgileri")

        # Ana frame
        main_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Sol taraf - Tanımlı daireler
        left_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=0)

        # Başlık
        title_label = ctk.CTkLabel(
            left_frame,
            text="Tanımlı Daireler",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(10, 5))

        # Grid layout için saf tkinter frame oluştur (TTk uyumluluğu için)
        tree_frame = tk.Frame(left_frame, bg=self.colors["background"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Daire listesi
        self.daire_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "lojman", "blok", "daire_no", "kullanim", "kat", "oda", "kiraya_esas", "isitilan", "tahsis", "isinma", "aidat", "katki", "aciklama"),
            show="headings",
            height=15
        )

        # Kolon başlıkları
        self.daire_tree.heading("id", text="ID")
        self.daire_tree.heading("lojman", text="Lojman")
        self.daire_tree.heading("blok", text="Blok")
        self.daire_tree.heading("daire_no", text="Daire No")
        self.daire_tree.heading("kullanim", text="Kullanım")
        self.daire_tree.heading("kat", text="Kat")
        self.daire_tree.heading("oda", text="Oda")
        self.daire_tree.heading("kiraya_esas", text="Kiraya Esas (m²)")
        self.daire_tree.heading("isitilan", text="Isıtılan (m²)")
        self.daire_tree.heading("tahsis", text="Tahsis Durumu")
        self.daire_tree.heading("isinma", text="Isınma Tipi")
        self.daire_tree.heading("aidat", text="Güncel Aidat")
        self.daire_tree.heading("katki", text="Katkı Payı")
        self.daire_tree.heading("aciklama", text="Açıklama")

        # Kolon genişlikleri ve ortalaması
        self.daire_tree.column("id", width=35, anchor="center")
        self.daire_tree.column("lojman", width=85, anchor="center")
        self.daire_tree.column("blok", width=40, anchor="center")
        self.daire_tree.column("daire_no", width=55, anchor="center")
        self.daire_tree.column("kullanim", width=60, anchor="center")
        self.daire_tree.column("kat", width=35, anchor="center")
        self.daire_tree.column("oda", width=40, anchor="center")
        self.daire_tree.column("kiraya_esas", width=70, anchor="center")
        self.daire_tree.column("isitilan", width=70, anchor="center")
        self.daire_tree.column("tahsis", width=85, anchor="center")
        self.daire_tree.column("isinma", width=75, anchor="center")
        self.daire_tree.column("aidat", width=75, anchor="center")
        self.daire_tree.column("katki", width=75, anchor="center")
        self.daire_tree.column("aciklama", width=100, anchor="center")

        # Scrollbars - Hem dikey hem yatay
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.daire_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.daire_tree.xview)
        self.daire_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.daire_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Sağ tık menüsü
        self.daire_context_menu = tk.Menu(self.daire_tree, tearoff=0)
        self.daire_context_menu.add_command(label="Düzenle", command=self.edit_daire)
        self.daire_context_menu.add_command(label="Sil", command=self.delete_daire)
        self.daire_tree.bind("<Button-3>", self.show_daire_context_menu)

        # Sağ taraf - Yeni daire ekleme
        right_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=0)

        # Başlık
        add_title = ctk.CTkLabel(
            right_frame,
            text="Yeni Daire Ekle",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        add_title.pack(pady=(10, 15))

        # Form - Scrollable frame kullanacağız
        scrollable_frame = ctk.CTkScrollableFrame(right_frame, fg_color=self.colors["surface"])
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Bağlı blok
        blok_label = ctk.CTkLabel(scrollable_frame, text="Bağlı Blok:", text_color=self.colors["text"])
        blok_label.pack(anchor="w", padx=20, pady=(20, 5))

        self.daire_blok_combo = ctk.CTkComboBox(scrollable_frame, values=[])
        self.daire_blok_combo.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_blok_combo.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_blok_combo))

        # Daire no
        no_label = ctk.CTkLabel(scrollable_frame, text="Daire No:", text_color=self.colors["text"])
        no_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_no_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 101")
        self.daire_no_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_no_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_no_entry))

        # Kullanım durumu (salt okunur)
        kullanim_label = ctk.CTkLabel(scrollable_frame, text="Kullanım Durumu:", text_color=self.colors["text"])
        kullanim_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_kullanim_label = ctk.CTkLabel(scrollable_frame, text="Boş", text_color=self.colors["text_secondary"])
        self.daire_kullanim_label.pack(anchor="w", padx=20, pady=(0, 15))

        # Oda sayısı
        oda_label = ctk.CTkLabel(scrollable_frame, text="Oda Sayısı:", text_color=self.colors["text"])
        oda_label.pack(anchor="w", padx=20, pady=(0, 5))

        # Oda sayısı için combobox (açılır liste) ekleyelim
        oda_options = ["1+1", "2+1", "3+1", "4+1", "5+1", "6+1", "7+1", "8+1", "Stüdyo", "Diğer"]
        self.daire_oda_combo = ctk.CTkComboBox(scrollable_frame, values=oda_options)
        # Varsayılan olarak ilk değeri seçelim
        if oda_options:
            self.daire_oda_combo.set(oda_options[0])
        self.daire_oda_combo.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_oda_combo.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_oda_combo))

        # Bulunduğu kat
        kat_label = ctk.CTkLabel(scrollable_frame, text="Bulunduğu Kat:", text_color=self.colors["text"])
        kat_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_kat_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 1")
        self.daire_kat_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_kat_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_kat_entry))

        # Kiraya esas alan
        kiraya_label = ctk.CTkLabel(scrollable_frame, text="Kiraya Esas Alan (m²):", text_color=self.colors["text"])
        kiraya_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_kiraya_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 85.5")
        self.daire_kiraya_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_kiraya_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_kiraya_entry))

        # Isıtılan alan
        isitilan_label = ctk.CTkLabel(scrollable_frame, text="Isıtılan Alan (m²):", text_color=self.colors["text"])
        isitilan_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_isitilan_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 85.5")
        self.daire_isitilan_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_isitilan_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_isitilan_entry))

        # Tahsis durumu
        tahsis_label = ctk.CTkLabel(scrollable_frame, text="Tahsis Durumu:", text_color=self.colors["text"])
        tahsis_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_tahsis_combo = ctk.CTkComboBox(
            scrollable_frame,
            values=["Subay", "Astsubay", "Uzman Erbaş", "Sivil Memur", "İşçi", "Boş"]
        )
        self.daire_tahsis_combo.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_tahsis_combo.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_tahsis_combo))

        # Isınma tipi
        isinma_label = ctk.CTkLabel(scrollable_frame, text="Isınma Tipi:", text_color=self.colors["text"])
        isinma_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_isinma_combo = ctk.CTkComboBox(
            scrollable_frame,
            values=["Merkezi Isıtma", "Bireysel", "Bölgesel", "Alternatif"]
        )
        self.daire_isinma_combo.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_isinma_combo.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_isinma_combo))

        # Güncel aidat
        aidat_label = ctk.CTkLabel(scrollable_frame, text="Güncel Aidat Tutarı (₺):", text_color=self.colors["text"])
        aidat_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_aidat_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 1500.00")
        self.daire_aidat_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_aidat_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_aidat_entry))

        # Katkı payı
        katki_label = ctk.CTkLabel(scrollable_frame, text="Katkı Payı Tutarı (₺):", text_color=self.colors["text"])
        katki_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_katki_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 500.00")
        self.daire_katki_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_katki_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_katki_entry))

        # Açıklama
        aciklama_label = ctk.CTkLabel(scrollable_frame, text="Açıklama (Opsiyonel):", text_color=self.colors["text"])
        aciklama_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_aciklama_textbox = ctk.CTkTextbox(scrollable_frame, height=60)
        self.daire_aciklama_textbox.pack(fill="x", padx=20, pady=(0, 20))
        self.daire_aciklama_textbox.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_aciklama_textbox))

        # Ekle butonu
        add_button = ctk.CTkButton(
            scrollable_frame,
            text="Daire Ekle",
            command=self.add_daire,
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"],
            height=40
        )
        add_button.pack(pady=(0, 20))

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_lojmanlar()
        self.load_bloklar()
        self.load_daireler()
        self.update_lojman_combo()
        self.update_blok_combo()

    def load_lojmanlar(self) -> None:
        """Lojmanları yükle"""
        # Treeview'i temizle
        for item in self.lojman_tree.get_children():
            self.lojman_tree.delete(item)

        self.lojmanlar = self.lojman_controller.get_all_with_details()

        for lojman in self.lojmanlar:
            self.lojman_tree.insert("", "end", values=(
                lojman.id,
                lojman.ad,
                lojman.adres,
                lojman.blok_sayisi,
                lojman.toplam_daire_sayisi,
                f"{lojman.toplam_kiraya_esas_alan:.1f}",
                f"{lojman.toplam_isitilan_alan:.1f}"
            ))

    def load_bloklar(self) -> None:
        """Blokları yükle"""
        # Treeview'i temizle
        for item in self.blok_tree.get_children():
            self.blok_tree.delete(item)

        self.bloklar = self.blok_controller.get_all_with_details()

        for blok in self.bloklar:
            self.blok_tree.insert("", "end", values=(
                blok.id,
                blok.lojman.ad,
                blok.ad,
                blok.kat_sayisi,
                blok.giris_kapi_no or "",
                blok.daire_sayisi,
                f"{blok.toplam_kiraya_esas_alan:.1f}",
                f"{blok.toplam_isitilan_alan:.1f}",
                blok.notlar or ""
            ))

    def load_daireler(self) -> None:
        """Daireleri yükle"""
        # Treeview'i temizle
        for item in self.daire_tree.get_children():
            self.daire_tree.delete(item)

        self.daireler = self.daire_controller.get_all_with_details()

        for daire in self.daireler:
            self.daire_tree.insert("", "end", values=(
                daire.id,
                daire.blok.lojman.ad,
                daire.blok.ad,
                daire.daire_no,
                daire.kullanim_durumu,
                daire.kat,
                self.convert_room_count_to_display(daire.oda_sayisi),
                f"{daire.kiraya_esas_alan:.1f}" if daire.kiraya_esas_alan else "",
                f"{daire.isitilan_alan:.1f}" if daire.isitilan_alan else "",
                daire.tahsis_durumu or "",
                daire.isinma_tipi or "",
                f"{daire.guncel_aidat:.2f} ₺" if daire.guncel_aidat else "0.00 ₺",
                f"{daire.katki_payi:.2f} ₺" if daire.katki_payi else "0.00 ₺",
                daire.aciklama or ""
            ))

    def convert_room_count_to_display(self, oda_sayisi: int) -> str:
        """Convert room count number to display format (1 -> 1+1, 2 -> 2+1, etc.)"""
        if oda_sayisi == 1:
            return "1+1"
        elif oda_sayisi == 2:
            return "2+1"
        elif oda_sayisi == 3:
            return "3+1"
        elif oda_sayisi == 4:
            return "4+1"
        elif oda_sayisi == 5:
            return "5+1"
        elif oda_sayisi == 6:
            return "6+1"
        elif oda_sayisi == 7:
            return "7+1"
        elif oda_sayisi == 8:
            return "8+1"
        else:
            # For other values, we'll use the "Diğer" format
            return f"{oda_sayisi}+1"

    def update_lojman_combo(self) -> None:
        """Lojman combo box'ını güncelle"""
        lojman_names = [lojman.ad for lojman in self.lojmanlar]
        self.blok_lojman_combo.configure(values=lojman_names)
        if lojman_names:
            self.blok_lojman_combo.set(lojman_names[0])

    def update_blok_combo(self) -> None:
        """Blok combo box'ını güncelle"""
        blok_options = []
        for blok in self.bloklar:
            blok_options.append(f"{blok.lojman.ad} - {blok.ad} Blok")

        self.daire_blok_combo.configure(values=blok_options)
        if blok_options:
            self.daire_blok_combo.set(blok_options[0])

    def add_lojman(self) -> None:
        """Yeni lojman ekle"""
        try:
            ad = self.lojman_name_entry.get().strip()
            adres = self.lojman_adres_textbox.get("1.0", "end").strip()
        except tk.TclError:
            return

        # UI Validation
        ad = UIValidator.validate_text_entry(self.lojman_name_entry, "Lojman Adı", 2, 100)
        if ad is None:
            return
            
        adres = UIValidator.validate_text_entry(self.lojman_adres_textbox, "Adres", 1, 500)
        if adres is None:
            return

        with ErrorHandler(parent=self.frame, show_success_msg=False):
             # Lojmanı oluştur
             lojman_data = {
                 "ad": ad,
                 "adres": adres
             }
             new_lojman = self.lojman_controller.create(lojman_data)
             self.show_message(f"Lojman '{new_lojman.ad}' başarıyla eklendi!")

             # Listeyi yenile
             self.load_data()

        # Formu temizle
        self.lojman_name_entry.delete(0, "end")
        self.lojman_adres_textbox.delete("1.0", "end")

    def add_blok(self) -> None:
        """Yeni blok ekle"""
        try:
            lojman_ad = self.blok_lojman_combo.get()
            blok_ad = self.blok_ad_entry.get().strip()
            kat_sayisi = self.blok_kat_entry.get().strip()
            giris_kapi = self.blok_giris_entry.get().strip()
            notlar = self.blok_not_textbox.get("1.0", "end").strip()
        except tk.TclError:
            return

        # UI Validation
        lojman_ad = UIValidator.validate_combobox(self.blok_lojman_combo, "Lojman")
        if lojman_ad is None:
            return
            
        blok_ad = UIValidator.validate_text_entry(self.blok_ad_entry, "Blok Adı", 1, 50)
        if blok_ad is None:
            return
            
        kat_sayisi = UIValidator.validate_number_entry(self.blok_kat_entry, "Kat Sayısı", allow_negative=False)
        if kat_sayisi is None:
            return

        with ErrorHandler(parent=self.frame, show_success_msg=False):
             # Lojmanı bul
             lojman = self.lojman_controller.get_by_ad(lojman_ad)
             if not lojman:
                 from models.exceptions import NotFoundError
                 raise NotFoundError("Seçilen lojman bulunamadı", code="NOT_FOUND_001")

             # Bloğu oluştur
             blok_data = {
                 "lojman_id": lojman.id,
                 "ad": blok_ad,
                 "kat_sayisi": int(kat_sayisi),
                 "giris_kapi_no": giris_kapi if giris_kapi else None,
                 "notlar": notlar if notlar else None
             }
             new_blok = self.blok_controller.create(blok_data)
             self.show_message(f"Blok '{new_blok.ad}' başarıyla eklendi!")

             # Listeyi yenile
             self.load_data()

        # Formu temizle
        self.blok_ad_entry.delete(0, "end")
        self.blok_kat_entry.delete(0, "end")
        self.blok_giris_entry.delete(0, "end")
        self.blok_not_textbox.delete("1.0", "end")

    def add_daire(self) -> None:
        """Yeni daire ekle"""
        try:
            # Widget'ların hala valid olup olmadığını kontrol et
            blok_option = self.daire_blok_combo.get()
            daire_no = self.daire_no_entry.get().strip()
            # Oda sayısını combobox'tan alalım
            oda_secimi = self.daire_oda_combo.get().strip()
            kat = self.daire_kat_entry.get().strip()
            kiraya_esas = self.daire_kiraya_entry.get().strip()
            isitilan = self.daire_isitilan_entry.get().strip()
            tahsis_durumu = self.daire_tahsis_combo.get()
            isinma_tipi = self.daire_isinma_combo.get()
            guncel_aidat = self.daire_aidat_entry.get().strip()
            katki_payi = self.daire_katki_entry.get().strip()
            aciklama = self.daire_aciklama_textbox.get("1.0", "end").strip()
        except tk.TclError:
            # Widget'lar destroy edilmiş, işlemi iptal et
            return

        # UI Validation
        blok_option = UIValidator.validate_combobox(self.daire_blok_combo, "Blok")
        if blok_option is None:
            return
            
        daire_no = UIValidator.validate_text_entry(self.daire_no_entry, "Daire Numarası", 1, 20)
        if daire_no is None:
            return
            
        oda_secimi = UIValidator.validate_combobox(self.daire_oda_combo, "Oda Sayısı")
        if oda_secimi is None:
            return
            
        kat = UIValidator.validate_number_entry(self.daire_kat_entry, "Kat", allow_negative=False)
        if kat is None:
            return
            
        kiraya_esas = UIValidator.validate_number_entry(self.daire_kiraya_entry, "Kiraya Esas Alan", allow_negative=False)
        if kiraya_esas is None:
            return
            
        isitilan = UIValidator.validate_number_entry(self.daire_isitilan_entry, "Isıtılan Alan", allow_negative=False)
        if isitilan is None:
            return
            
        guncel_aidat = UIValidator.validate_number_entry(self.daire_aidat_entry, "Güncel Aidat", allow_negative=False)
        if guncel_aidat is None:
            return
            
        katki_payi = UIValidator.validate_number_entry(self.daire_katki_entry, "Katkı Payı", allow_negative=False)
        if katki_payi is None:
            return

        with ErrorHandler(parent=self.frame, show_success_msg=False):
             # Blok option'ından lojman ve blok adlarını çıkar
             # Format: "Lojman Adı - Blok Adı Blok"
             if " - " not in blok_option:
                 from models.exceptions import ValidationError
                 raise ValidationError("Blok seçimi geçersiz!", code="VAL_001")

             lojman_ad, blok_part = blok_option.split(" - ", 1)
             blok_ad = blok_part.replace(" Blok", "").strip()

             # Lojmanı bul
             lojman = self.lojman_controller.get_by_ad(lojman_ad)
             if not lojman:
                 from models.exceptions import NotFoundError
                 raise NotFoundError("Seçilen lojman bulunamadı", code="NOT_FOUND_001")

             # Bloğu bul
             blok = self.blok_controller.get_by_ad_and_lojman(blok_ad, lojman.id)
             if not blok:
                 from models.exceptions import NotFoundError
                 raise NotFoundError("Seçilen blok bulunamadı", code="NOT_FOUND_001")

             # Oda sayısını sayıya dönüştür
             if oda_secimi == "Stüdyo":
                 oda_sayisi = 1
             elif oda_secimi == "Diğer":
                 # Diğer seçildiğinde varsayılan olarak 3 oda ayarlayalım
                 oda_sayisi = 3
             else:
                 # "1+1", "2+1", vb. formatında
                 try:
                     oda_sayisi = int(oda_secimi.split("+")[0])
                 except ValueError:
                     from models.exceptions import ValidationError
                     raise ValidationError("Geçersiz oda sayısı formatı!", code="VAL_002")

             # Sayısal değerleri dönüştür
             kat = int(kat) if kat else 1
             kiraya_esas = float(kiraya_esas) if kiraya_esas else 0.0
             isitilan = float(isitilan) if isitilan else 0.0
             guncel_aidat = float(guncel_aidat) if guncel_aidat else 0.0
             katki_payi = float(katki_payi) if katki_payi else 0.0

             # Daireyi oluştur
             daire_data = {
                 "blok_id": blok.id,
                 "daire_no": daire_no,
                 "oda_sayisi": oda_sayisi,
                 "kat": kat,
                 "kiraya_esas_alan": kiraya_esas,
                 "isitilan_alan": isitilan,
                 "tahsis_durumu": tahsis_durumu if tahsis_durumu else None,
                 "isinma_tipi": isinma_tipi if isinma_tipi else None,
                 "guncel_aidat": guncel_aidat,
                 "katki_payi": katki_payi,
                 "aciklama": aciklama if aciklama else None
             }
             new_daire = self.daire_controller.create(daire_data)
             self.show_message(f"Daire '{new_daire.daire_no}' başarıyla eklendi!")

             # Listeyi yenile
             self.load_data()

        # Formu temizle
        self.daire_no_entry.delete(0, "end")
        # Oda combobox'ını varsayılan değere getir
        if self.daire_oda_combo.cget("values"):
            self.daire_oda_combo.set(self.daire_oda_combo.cget("values")[0])
        self.daire_kat_entry.delete(0, "end")
        self.daire_kiraya_entry.delete(0, "end")
        self.daire_isitilan_entry.delete(0, "end")
        self.daire_aidat_entry.delete(0, "end")
        self.daire_katki_entry.delete(0, "end")
        self.daire_aciklama_textbox.delete("1.0", "end")

    # Context menu fonksiyonları
    def show_lojman_context_menu(self, event: tk.Event) -> None:
        """Lojman tree için sağ tık menüsünü göster"""
        try:
            item = self.lojman_tree.identify_row(event.y)
            if item:
                self.lojman_tree.selection_set(item)
                self.lojman_context_menu.post(event.x_root, event.y_root)
        except:
            pass

    def show_blok_context_menu(self, event: tk.Event) -> None:
        """Blok tree için sağ tık menüsünü göster"""
        try:
            item = self.blok_tree.identify_row(event.y)
            if item:
                self.blok_tree.selection_set(item)
                self.blok_context_menu.post(event.x_root, event.y_root)
        except:
            pass

    def show_daire_context_menu(self, event: tk.Event) -> None:
        """Daire tree için sağ tık menüsünü göster"""
        try:
            item = self.daire_tree.identify_row(event.y)
            if item:
                self.daire_tree.selection_set(item)
                self.daire_context_menu.post(event.x_root, event.y_root)
        except:
            pass

    # Düzenleme fonksiyonları
    def edit_lojman(self) -> None:
        """Seçili lojmanı düzenle"""
        selection = self.lojman_tree.selection()
        if not selection:
            self.show_error("Lütfen düzenlemek istediğiniz lojmanı seçin!")
            return

        item = selection[0]
        values = self.lojman_tree.item(item, "values")
        lojman_id = int(values[0])  # String'i integer'a çevir

        # Lojmanı bul
        lojman = self.lojman_controller.get_by_id(lojman_id)
        if not lojman:
            self.show_error("Lojman bulunamadı!")
            return

        # Düzenleme modal'ı aç
        self.show_edit_lojman_modal(lojman)

    def edit_blok(self) -> None:
        """Seçili bloğu düzenle"""
        selection = self.blok_tree.selection()
        if not selection:
            self.show_error("Lütfen düzenlemek istediğiniz bloğu seçin!")
            return

        item = selection[0]
        values = self.blok_tree.item(item, "values")
        blok_id = int(values[0])  # String'i integer'a çevir

        # Bloğu bul
        blok = self.blok_controller.get_by_id(blok_id)
        if not blok:
            self.show_error("Blok bulunamadı!")
            return

        # Düzenleme modal'ı aç
        self.show_edit_blok_modal(blok)

    def edit_daire(self) -> None:
        """Seçili daireyi düzenle"""
        selection = self.daire_tree.selection()
        if not selection:
            self.show_error("Lütfen düzenlemek istediğiniz daireyi seçin!")
            return

        item = selection[0]
        values = self.daire_tree.item(item, "values")
        daire_id = int(values[0])  # String'i integer'a çevir

        # Daireyi bul
        daire = self.daire_controller.get_by_id(daire_id)
        if not daire:
            self.show_error("Daire bulunamadı!")
            return

        # Düzenleme modal'ı aç
        self.show_edit_daire_modal(daire)

    # Silme fonksiyonları
    def delete_lojman(self) -> None:
        """Seçili lojmanı sil"""
        selection = self.lojman_tree.selection()
        if not selection:
            self.show_error("Lütfen silmek istediğiniz lojmanı seçin!")
            return

        item = selection[0]
        values = self.lojman_tree.item(item, "values")
        lojman_id = int(values[0])  # String'i integer'a çevir
        lojman_ad = values[1]

        # Onay al
        if not self.ask_yes_no(f"'{lojman_ad}' lojmanını silmek istediğinizden emin misiniz? Bu işlem geri alınamaz!", "Silme Onayı"):
            return

        try:
            success = self.lojman_controller.delete(lojman_id)
            if success:
                self.show_message(f"'{lojman_ad}' lojmanı başarıyla silindi!")
                self.load_data()
            else:
                self.show_error("Lojman silinirken hata oluştu!")
        except Exception as e:
            self.show_error(f"Lojman silinirken hata oluştu: {str(e)}")

    def delete_blok(self) -> None:
        """Seçili bloğu sil"""
        selection = self.blok_tree.selection()
        if not selection:
            self.show_error("Lütfen silmek istediğiniz bloğu seçin!")
            return

        item = selection[0]
        values = self.blok_tree.item(item, "values")
        blok_id = int(values[0])  # String'i integer'a çevir
        blok_ad = values[2]

        # Onay al
        if not self.ask_yes_no(f"'{blok_ad}' bloğunu silmek istediğinizden emin misiniz? Bu işlem geri alınamaz!", "Silme Onayı"):
            return

        try:
            success = self.blok_controller.delete(blok_id)
            if success:
                self.show_message(f"'{blok_ad}' bloğu başarıyla silindi!")
                self.load_data()
            else:
                self.show_error("Blok silinirken hata oluştu!")
        except Exception as e:
            self.show_error(f"Blok silinirken hata oluştu: {str(e)}")

    def delete_daire(self) -> None:
        """Seçili daireyi sil"""
        selection = self.daire_tree.selection()
        if not selection:
            self.show_error("Lütfen silmek istediğiniz daireyi seçin!")
            return

        item = selection[0]
        values = self.daire_tree.item(item, "values")
        daire_id = int(values[0])  # String'i integer'a çevir
        daire_no = values[3]

        # Onay al
        if not self.ask_yes_no(f"'{daire_no}' dairesini silmek istediğinizden emin misiniz? Bu işlem geri alınamaz!", "Silme Onayı"):
            return

        try:
            success = self.daire_controller.delete(daire_id)
            if success:
                self.show_message(f"'{daire_no}' dairesi başarıyla silindi!")
                self.load_data()
            else:
                self.show_error("Daire silinirken hata oluştu!")
        except Exception as e:
            self.show_error(f"Daire silinirken hata oluştu: {str(e)}")

    # Düzenleme modal'ları
    def show_edit_lojman_modal(self, lojman: Lojman) -> None:
        """Lojman düzenleme modal'ı göster"""
        modal = ctk.CTkToplevel(self.parent)
        modal.title("Lojman Düzenle")
        modal.geometry("400x376")
        modal.transient(self.parent)
        modal.lift()
        modal.focus_force()

        # Başlık
        title_label = ctk.CTkLabel(
            modal,
            text="Lojman Düzenle",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(20, 10))

        # Form frame
        form_frame = ctk.CTkFrame(modal, fg_color=self.colors["surface"])
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Lojman adı
        name_label = ctk.CTkLabel(form_frame, text="Lojman Adı:", text_color=self.colors["text"])
        name_label.pack(anchor="w", padx=20, pady=(20, 5))

        name_entry = ctk.CTkEntry(form_frame)
        name_entry.insert(0, lojman.ad)
        name_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Adres
        adres_label = ctk.CTkLabel(form_frame, text="Adres:", text_color=self.colors["text"])
        adres_label.pack(anchor="w", padx=20, pady=(0, 5))

        adres_textbox = ctk.CTkTextbox(form_frame, height=80)
        adres_textbox.insert("1.0", lojman.adres)
        adres_textbox.pack(fill="x", padx=20, pady=(0, 20))

        # Butonlar
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        def save_lojman() -> None:
            """Lojman verilerini kaydet"""
            ad = name_entry.get().strip()
            adres = adres_textbox.get("1.0", "end").strip()

            # Form validasyonu
            ad = UIValidator.validate_text_entry(name_entry, "Lojman Adı", 2, 100)
            if ad is None:
                return

            adres = UIValidator.validate_text_entry(adres_textbox, "Adres", 1, 500)
            if adres is None:
                return

            try:
                with ErrorHandler(parent=modal, show_success_msg=False):
                    self.lojman_controller.update(lojman.id, {"ad": ad, "adres": adres})
                    modal.destroy()
                    show_success(parent=self.parent, title="Başarılı", message=f"Lojman '{ad}' başarıyla güncellendi!")
                    self.load_data()
            except (ValidationError, DatabaseError) as e:
                handle_exception(e, parent=modal)
            except Exception as e:
                handle_exception(e, parent=modal)

        def cancel() -> None:
            modal.destroy()

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="İptal",
            command=cancel,
            fg_color=self.colors["text_secondary"],
            hover_color=self.colors["border"]
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Kaydet",
            command=save_lojman,
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"]
        )
        save_btn.pack(side="right")

    def show_edit_blok_modal(self, blok: Blok) -> None:
        """Blok düzenleme modal'ı göster"""
        modal = ctk.CTkToplevel(self.parent)
        modal.title("Blok Düzenle")
        modal.geometry("400x513")
        modal.transient(self.parent)
        modal.lift()
        modal.focus_force()

        # Başlık
        title_label = ctk.CTkLabel(
            modal,
            text="Blok Düzenle",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(20, 10))

        # Form frame
        form_frame = ctk.CTkFrame(modal, fg_color=self.colors["surface"])
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Blok adı
        name_label = ctk.CTkLabel(form_frame, text="Blok Adı:", text_color=self.colors["text"])
        name_label.pack(anchor="w", padx=20, pady=(20, 5))

        name_entry = ctk.CTkEntry(form_frame)
        name_entry.insert(0, blok.ad)
        name_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Kat sayısı
        kat_label = ctk.CTkLabel(form_frame, text="Kat Sayısı:", text_color=self.colors["text"])
        kat_label.pack(anchor="w", padx=20, pady=(0, 5))

        kat_entry = ctk.CTkEntry(form_frame)
        kat_entry.insert(0, str(blok.kat_sayisi))
        kat_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Giriş kapı no
        giris_label = ctk.CTkLabel(form_frame, text="Giriş Kapı No:", text_color=self.colors["text"])
        giris_label.pack(anchor="w", padx=20, pady=(0, 5))

        giris_entry = ctk.CTkEntry(form_frame)
        if blok.giris_kapi_no:
            giris_entry.insert(0, blok.giris_kapi_no)
        giris_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Notlar
        not_label = ctk.CTkLabel(form_frame, text="Notlar:", text_color=self.colors["text"])
        not_label.pack(anchor="w", padx=20, pady=(0, 5))

        not_textbox = ctk.CTkTextbox(form_frame, height=60)
        if blok.notlar:
            not_textbox.insert("1.0", blok.notlar)
        not_textbox.pack(fill="x", padx=20, pady=(0, 20))

        # Butonlar
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        def save_blok() -> None:
            """Blok verilerini kaydet"""
            # Form validasyonu
            ad = UIValidator.validate_text_entry(name_entry, "Blok Adı", 2, 50)
            if ad is None:
                return

            kat_sayisi = UIValidator.validate_number_entry(kat_entry, "Kat Sayısı", allow_negative=False)
            if kat_sayisi is None:
                return

            giris_kapi = giris_entry.get().strip()
            notlar = not_textbox.get("1.0", "end").strip()

            try:
                with ErrorHandler(parent=modal, show_success_msg=False):
                    update_data = {
                        "ad": ad,
                        "kat_sayisi": int(kat_sayisi),
                        "giris_kapi_no": giris_kapi if giris_kapi else None,
                        "notlar": notlar if notlar else None
                    }
                    self.blok_controller.update(blok.id, update_data)
                    modal.destroy()
                    show_success(parent=self.parent, title="Başarılı", message=f"Blok '{ad}' başarıyla güncellendi!")
                    self.load_data()
            except (ValidationError, DatabaseError, NotFoundError) as e:
                handle_exception(e, parent=modal)
            except Exception as e:
                handle_exception(e, parent=modal)

        def cancel() -> None:
            modal.destroy()

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="İptal",
            command=cancel,
            fg_color=self.colors["text_secondary"],
            hover_color=self.colors["border"]
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Kaydet",
            command=save_blok,
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"]
        )
        save_btn.pack(side="right")

    

        
    def show_edit_daire_modal(self, daire: Daire) -> None:
        """Daire düzenleme modal'ı göster"""
        modal = ctk.CTkToplevel(self.parent)
        modal.title("Daire Düzenle")
        modal.geometry("500x600")
        modal.transient(self.parent)
        modal.lift()
        modal.focus_force()

        # Başlık
        title_label = ctk.CTkLabel(
            modal,
            text="Daire Düzenle",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(20, 10))

        # Scrollable form
        scrollable_frame = ctk.CTkScrollableFrame(modal, fg_color=self.colors["surface"])
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Daire no
        no_label = ctk.CTkLabel(scrollable_frame, text="Daire No:", text_color=self.colors["text"])
        no_label.pack(anchor="w", padx=20, pady=(20, 5))

        no_entry = ctk.CTkEntry(scrollable_frame)
        no_entry.insert(0, daire.daire_no)
        no_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Oda sayısı
        oda_label = ctk.CTkLabel(scrollable_frame, text="Oda Sayısı:", text_color=self.colors["text"])
        oda_label.pack(anchor="w", padx=20, pady=(0, 5))

        # Oda sayısı için combobox (açılır liste) ekleyelim
        oda_options = ["1+1", "2+1", "3+1", "4+1", "5+1", "6+1", "7+1", "8+1", "Stüdyo", "Diğer"]
        oda_combo = ctk.CTkComboBox(scrollable_frame, values=oda_options)
        # Mevcut oda sayısını ayarla
        current_oda_display = self.convert_room_count_to_display(daire.oda_sayisi)
        if current_oda_display in oda_options:
            oda_combo.set(current_oda_display)
        elif oda_options:
            oda_combo.set(oda_options[0])
        oda_combo.pack(fill="x", padx=20, pady=(0, 15))
        oda_combo.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, oda_combo))

        # Bulunduğu kat
        kat_label = ctk.CTkLabel(scrollable_frame, text="Bulunduğu Kat:", text_color=self.colors["text"])
        kat_label.pack(anchor="w", padx=20, pady=(0, 5))

        kat_entry = ctk.CTkEntry(scrollable_frame)
        kat_entry.insert(0, str(daire.kat))
        kat_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Kiraya esas alan
        kiraya_label = ctk.CTkLabel(scrollable_frame, text="Kiraya Esas Alan (m²):", text_color=self.colors["text"])
        kiraya_label.pack(anchor="w", padx=20, pady=(0, 5))

        kiraya_entry = ctk.CTkEntry(scrollable_frame)
        if daire.kiraya_esas_alan:
            kiraya_entry.insert(0, str(daire.kiraya_esas_alan))
        kiraya_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Isıtılan alan
        isitilan_label = ctk.CTkLabel(scrollable_frame, text="Isıtılan Alan (m²):", text_color=self.colors["text"])
        isitilan_label.pack(anchor="w", padx=20, pady=(0, 5))

        isitilan_entry = ctk.CTkEntry(scrollable_frame)
        if daire.isitilan_alan:
            isitilan_entry.insert(0, str(daire.isitilan_alan))
        isitilan_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Tahsis durumu
        tahsis_label = ctk.CTkLabel(scrollable_frame, text="Tahsis Durumu:", text_color=self.colors["text"])
        tahsis_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_tahsis_combo = ctk.CTkComboBox(
        scrollable_frame,
        values=["Subay", "Astsubay", "Uzman Erbaş", "Sivil Memur", "İşçi", "Boş"]
        )
        self.daire_tahsis_combo.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_tahsis_combo.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_tahsis_combo))
        self.daire_tahsis_combo.set(daire.tahsis_durumu)

        # Isınma tipi
        isinma_label = ctk.CTkLabel(scrollable_frame, text="Isınma Tipi:", text_color=self.colors["text"])
        isinma_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_isinma_combo = ctk.CTkComboBox(
        scrollable_frame,
        values=["Merkezi Isıtma", "Bireysel", "Bölgesel", "Alternatif"]
        )
        self.daire_isinma_combo.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_isinma_combo.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_isinma_combo))
        self.daire_isinma_combo.set(daire.isinma_tipi)

        # Güncel aidat
        aidat_label = ctk.CTkLabel(scrollable_frame, text="Güncel Aidat Tutarı (₺):", text_color=self.colors["text"])
        aidat_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_aidat_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 1500.00")
        self.daire_aidat_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_aidat_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_aidat_entry))
        self.daire_aidat_entry.insert(0, str(daire.guncel_aidat))

        # Katkı payı
        katki_label = ctk.CTkLabel(scrollable_frame, text="Katkı Payı Tutarı (₺):", text_color=self.colors["text"])
        katki_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_katki_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Örn: 500.00")
        self.daire_katki_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.daire_katki_entry.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_katki_entry))
        self.daire_katki_entry.insert(0, str(daire.katki_payi))

        # Açıklama
        aciklama_label = ctk.CTkLabel(scrollable_frame, text="Açıklama (Opsiyonel):", text_color=self.colors["text"])
        aciklama_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daire_aciklama_textbox = ctk.CTkTextbox(scrollable_frame, height=60)
        if daire.aciklama:
            self.daire_aciklama_textbox.insert("1.0", daire.aciklama)
        self.daire_aciklama_textbox.pack(fill="x", padx=20, pady=(0, 20))
        self.daire_aciklama_textbox.bind("<FocusIn>", lambda e: self.scroll_to_widget(scrollable_frame, self.daire_aciklama_textbox))

        # Butonlar
        button_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        def save_daire() -> None:
            """Daire verilerini kaydet"""
            # Form validasyonu
            daire_no = UIValidator.validate_text_entry(no_entry, "Daire Numarası", 1, 20)
            if daire_no is None:
                return

            # Oda seçimi kontrolü
            oda_secimi = oda_combo.get().strip()
            if not oda_secimi:
                show_error(modal, "Oda sayısı seçilmelidir!")
                return

            # Oda sayısını sayıya dönüştür
            if oda_secimi == "Stüdyo":
                oda_sayisi = 1
            elif oda_secimi == "Diğer":
                oda_sayisi = 3
            else:
                try:
                    oda_sayisi = int(oda_secimi.split("+")[0])
                except ValueError:
                    show_error(modal, "Geçersiz oda sayısı formatı!")
                    return

            # Sayısal alan doğrulamları
            kat = UIValidator.validate_number_entry(kat_entry, "Kat", allow_negative=False)
            if kat is None:
                return

            kiraya_esas = UIValidator.validate_number_entry(kiraya_entry, "Kiraya Esas Alan", allow_negative=False)
            if kiraya_esas is None:
                return

            isitilan = UIValidator.validate_number_entry(isitilan_entry, "Isıtılan Alan", allow_negative=False)
            if isitilan is None:
                return

            guncel_aidat = UIValidator.validate_number_entry(self.daire_aidat_entry, "Güncel Aidat", allow_negative=False)
            if guncel_aidat is None:
                return

            katki_payi = UIValidator.validate_number_entry(self.daire_katki_entry, "Katkı Payı", allow_negative=False)
            if katki_payi is None:
                return

            tahsis_durumu = self.daire_tahsis_combo.get()
            isinma_tipi = self.daire_isinma_combo.get()
            aciklama = self.daire_aciklama_textbox.get("1.0", "end").strip()

            try:
                with ErrorHandler(parent=modal, show_success_msg=False):
                    update_data = {
                        "daire_no": daire_no,
                        "oda_sayisi": oda_sayisi,
                        "kat": int(kat),
                        "kiraya_esas_alan": float(kiraya_esas),
                        "isitilan_alan": float(isitilan),
                        "tahsis_durumu": tahsis_durumu if tahsis_durumu else None,
                        "isinma_tipi": isinma_tipi if isinma_tipi else None,
                        "guncel_aidat": float(guncel_aidat),
                        "katki_payi": float(katki_payi),
                        "aciklama": aciklama if aciklama else None
                    }
                    self.daire_controller.update(daire.id, update_data)
                    modal.destroy()
                    show_success(parent=self.parent, title="Başarılı", message=f"Daire '{daire_no}' başarıyla güncellendi!")
                    self.load_data()
            except (ValidationError, DatabaseError, NotFoundError) as e:
                handle_exception(e, parent=modal)
            except Exception as e:
                handle_exception(e, parent=modal)

        def cancel() -> None:
            modal.destroy()

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="İptal",
            command=cancel,
            fg_color=self.colors["text_secondary"],
            hover_color=self.colors["border"]
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Kaydet",
            command=save_daire,
            fg_color=self.colors["success"],
            hover_color=self.colors["primary"]
        )
        save_btn.pack(side="right")

    def scroll_to_widget(self, scrollable_frame: ctk.CTkScrollableFrame, widget: ctk.CTkBaseClass) -> None:
        """Scrollable frame'i widget'a kaydır
        
        Widget odaklandığında scrollable frame'i otomatik kaydırır.
        
        Args:
            scrollable_frame (ctk.CTkScrollableFrame): Kaydırılacak çerçeve
            widget (ctk.CTkBaseClass): Hedef widget
        """
        try:
            # Widget'ın y konumunu al
            widget_y = widget.winfo_y()

            # Scrollable frame'in canvas'ını bul
            canvas = None
            for child in scrollable_frame.winfo_children():
                if hasattr(child, 'yview_moveto'):
                    canvas = child
                    break

            if canvas:
                # İçerik yüksekliğini hesapla
                total_height = 0
                for child in scrollable_frame.winfo_children():
                    if hasattr(child, 'winfo_y') and hasattr(child, 'winfo_height'):
                        total_height = max(total_height, child.winfo_y() + child.winfo_height())

                # Frame yüksekliğini al
                frame_height = scrollable_frame.winfo_height()

                # Scroll pozisyonunu hesapla (widget'ı görünür alanın üstüne getir)
                if total_height > frame_height:
                    target_y = max(0, widget_y - 30)  # 30 pixel margin
                    scroll_fraction = target_y / (total_height - frame_height)
                    scroll_fraction = min(1.0, max(0.0, scroll_fraction))

                    canvas.yview_moveto(scroll_fraction)

        except Exception as e:
            # Hata olursa sessizce geç
            pass
