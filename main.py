#!/usr/bin/env python3
"""
Aidat Plus - Modern Lojman Yönetim Uygulaması
Offline çalışan, Python tabanlı lojman aidat yönetim sistemi
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import logging
from typing import Dict

# Proje klasörünü Python path'e ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration Manager'ı başlat
from configuration import ConfigurationManager, ConfigKeys
from utils.logger import AidatPlusLogger

config_mgr = ConfigurationManager.get_instance()

# Logging ayarlarını uygula (UTF-8 support ile)
logging_level = config_mgr.get(ConfigKeys.LOGGING_LEVEL, 'INFO')
logger_instance = AidatPlusLogger(
    name="AidatPlus",
    log_level=getattr(logging, logging_level)
)
logger = logger_instance.logger

logger.info("=== Aidat Plus başlatılıyor ===")
logger.info(f"Environment: {config_mgr.get(ConfigKeys.APP_ENV)}")
logger.info(f"Debug Mode: {config_mgr.get(ConfigKeys.APP_DEBUG)}")

# Modelleri import et ki tablolar oluşturulsun
from models.base import *

# Uygulama renk şeması (Resmi kurum renkleri - Light tema için)
# Dark mode CustomTkinter otomatik olarak uyarlanır
COLORS = {
    "primary": "#003366",      # Koyu mavi (ana renk)
    "secondary": "#0055A4",    # Orta mavi
    "accent": "#E6F3FF",       # Açık mavi
    "background": "#F8F9FA",   # Açık gri-beyaz (light) / Koyu gri (dark)
    "surface": "#FFFFFF",      # Beyaz (light) / Koyu (dark)
    "text": "#212529",         # Koyu gri metin (light) / Açık gri (dark)
    "text_secondary": "#6C757D", # Açık gri metin
    "border": "#DEE2E6",       # Kenarlık rengi
    "success": "#28A745",      # Yeşil
    "warning": "#FFC107",      # Sarı
    "error": "#DC3545"         # Kırmızı
}

class AidatPlusApp:
    """Ana uygulama sınıfı"""

    def __init__(self) -> None:
        """
        Ana uygulama sınıfını başlat.
        
        Configuration Manager'dan UI ayarlarını yükler,
        CustomTkinter'ı konfigüre eder, ana pencereyi oluşturur,
        ve arayüzü kurar.
        
        Konfigürasyon kaynakları:
        - config/app_config.json
        - config/user_preferences.json
        - .env dosyası
        """
        self.config = config_mgr
        
        # CustomTkinter ayarları (konfigürasyondan)
        theme = self.config.get(ConfigKeys.UI_THEME, 'dark')
        # CustomTkinter appearance modes: "dark", "light", "system"
        # theme config'ten gelen değer doğru olup olmadığını kontrol et
        if theme not in ('dark', 'light', 'system'):
            theme = 'dark'  # Default to dark
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")
        logger.debug(f"Theme set to: {theme}")

        # Ana pencere
        self.root = ctk.CTk()
        self.root.title("Aidat Plus - Lojman Yönetim Sistemi")
        self.root.resizable(False, False)
        
        # Ana pencereyi ekranın üst-ortasında konumlandır
        # Konfigürasyondan pencere boyutlarını al
        window_width = self.config.get(ConfigKeys.UI_DEFAULT_WIDTH, 1300)
        window_height = self.config.get(ConfigKeys.UI_DEFAULT_HEIGHT, 785)
        screen_width = self.root.winfo_screenwidth()
        x = (screen_width - window_width) // 2
        y = 0
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        logger.debug(f"Window geometry: {window_width}x{window_height}")

        # Icon ayarı (varsa)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except Exception as e:
            logger.debug(f"Icon not found: {e}")

        # Panel referansları
        self.panels: Dict[str, ctk.CTkToplevel] = {}

        self.setup_ui()

    def setup_ui(self) -> None:
        """Ana arayüzü oluştur"""
        # Ana container
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["background"])
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Üst başlık alanı
        header_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Başlık
        title_label = ctk.CTkLabel(
            header_frame,
            text="Aidat Plus",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["surface"]
        )
        title_label.pack(side="left", padx=30, pady=20)

        # Alt başlık
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Modern Lojman Yönetim Sistemi",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["accent"]
        )
        subtitle_label.pack(side="left", padx=(0, 30), pady=(40, 0))

        # Ana içerik alanı
        content_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["surface"])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Navigasyon butonları
        self.create_navigation_buttons(content_frame)

        # Dashboard panelini ana sayfada göster
        self.dashboard_container = ctk.CTkFrame(content_frame, fg_color=COLORS["surface"])
        self.dashboard_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Dashboard'u yükle
        self.load_dashboard_home()

    def create_navigation_buttons(self, parent: ctk.CTkFrame) -> None:
        """Navigasyon butonlarını oluştur"""
        nav_frame = ctk.CTkFrame(parent, fg_color=COLORS["background"], width=250)
        nav_frame.pack(side="left", fill="y", padx=(0, 20), pady=0)
        nav_frame.pack_propagate(False)

        # Navigasyon başlığı
        nav_title = ctk.CTkLabel(
            nav_frame,
            text="Modüller",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["primary"]
        )
        nav_title.pack(pady=(20, 10))

        # Buton verileri
        buttons_data = [
            ("Finans", "💰", self.open_finans_panel),
            ("Aidat", "💳", self.open_aidat_panel),
            ("Sakin", "👥", self.open_sakin_panel),
            ("Lojman", "🏠", self.open_lojman_panel),
            ("Raporlar", "📊", self.open_raporlar_panel),
            ("Ayarlar", "⚙️", self.open_ayarlar_panel)
        ]

        # Butonları oluştur
        for name, icon, command in buttons_data:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"{icon} {name}",
                command=command,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=COLORS["secondary"],
                hover_color=COLORS["primary"],
                height=50,
                width=200
            )
            btn.pack(pady=5, padx=20)

    def load_dashboard_home(self) -> None:
        """Ana sayfada dashboard'u yükle"""
        try:
            from ui.dashboard_panel import DashboardPanel
            DashboardPanel(self.dashboard_container, COLORS)
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.dashboard_container,
                text=f"Dashboard yükleme hatası: {str(e)}",
                text_color=COLORS["error"]
            )
            error_label.pack(expand=True)

    def open_dashboard_panel(self) -> None:
        """Dashboard panelini aç"""
        from ui.dashboard_panel import DashboardPanel

        # Eğer panel zaten açıksa, onu öne getir
        if "Dashboard" in self.panels:
            panel_window = self.panels["Dashboard"]
            if panel_window.winfo_exists():
                panel_window.lift()
                panel_window.focus_force()
                return

        # Yeni panel penceresi oluştur
        panel_window = ctk.CTkToplevel(self.root)
        panel_window.title(f"Aidat Plus - 📊 Dashboard")
        self.center_window(panel_window, 1400, 900)

        # Ana pencerenin önünde kalması için
        panel_window.transient(self.root)
        panel_window.lift()
        panel_window.focus_force()

        # Panel referansını sakla
        self.panels["Dashboard"] = panel_window

        # Panel kapatıldığında referansı temizle
        panel_window.protocol("WM_DELETE_WINDOW",
            lambda: self.close_panel("Dashboard", panel_window))

        # Panel başlığı
        header_frame = ctk.CTkFrame(panel_window, fg_color=COLORS["primary"], height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["surface"]
        )
        title_label.pack(pady=15)

        # Dashboard panelini oluştur
        DashboardPanel(panel_window, COLORS)

    def open_finans_panel(self) -> None:
        """Finans panelini aç"""
        from ui.finans_panel import FinansPanel

        # Eğer panel zaten açıksa, onu öne getir
        if "Finans" in self.panels:
            panel_window = self.panels["Finans"]
            if panel_window.winfo_exists():
                panel_window.lift()
                panel_window.focus_force()
                return

        # Yeni panel penceresi oluştur
        panel_window = ctk.CTkToplevel(self.root)
        panel_window.title(f"Aidat Plus - 💰 Finans Yönetimi")
        self.center_window(panel_window, 1200, 700)

        # Ana pencerenin önünde kalması için
        panel_window.transient(self.root)
        panel_window.lift()
        panel_window.focus_force()

        # Panel referansını sakla
        self.panels["Finans"] = panel_window

        # Panel kapatıldığında referansı temizle
        panel_window.protocol("WM_DELETE_WINDOW",
            lambda: self.close_panel("Finans", panel_window))

        # Panel başlığı
        header_frame = ctk.CTkFrame(panel_window, fg_color=COLORS["primary"], height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="💰 Finans Yönetimi",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["surface"]
        )
        title_label.pack(pady=15)

        # Finans panelini oluştur
        FinansPanel(panel_window, COLORS)

    def open_aidat_panel(self) -> None:
        """Aidat panelini aç"""
        from ui.aidat_panel import AidatPanel

        # Eğer panel zaten açıksa, onu öne getir
        if "Aidat" in self.panels:
            panel_window = self.panels["Aidat"]
            if panel_window.winfo_exists():
                panel_window.lift()
                panel_window.focus_force()
                return

        # Yeni panel penceresi oluştur
        panel_window = ctk.CTkToplevel(self.root)
        panel_window.title(f"Aidat Plus - 💳 Aidat Yönetimi")
        self.center_window(panel_window, 1200, 700)

        # Ana pencerenin önünde kalması için
        panel_window.transient(self.root)
        panel_window.lift()
        panel_window.focus_force()

        # Panel referansını sakla
        self.panels["Aidat"] = panel_window

        # Panel kapatıldığında referansı temizle
        panel_window.protocol("WM_DELETE_WINDOW",
            lambda: self.close_panel("Aidat", panel_window))

        # Panel başlığı
        header_frame = ctk.CTkFrame(panel_window, fg_color=COLORS["primary"], height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="💳 Aidat Yönetimi",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["surface"]
        )
        title_label.pack(pady=15)

        # Aidat panelini oluştur
        AidatPanel(panel_window, COLORS)

    def open_sakin_panel(self) -> None:
        """Sakin panelini aç"""
        from ui.sakin_panel import SakinPanel

        # Eğer panel zaten açıksa, onu öne getir
        if "Sakin" in self.panels:
            panel_window = self.panels["Sakin"]
            if panel_window.winfo_exists():
                panel_window.lift()
                panel_window.focus_force()
                return

        # Yeni panel penceresi oluştur
        panel_window = ctk.CTkToplevel(self.root)
        panel_window.title(f"Aidat Plus - 👥 Sakin Yönetimi")
        self.center_window(panel_window, 1200, 700)

        # Ana pencerenin önünde kalması için
        panel_window.transient(self.root)
        panel_window.lift()
        panel_window.focus_force()

        # Panel referansını sakla
        self.panels["Sakin"] = panel_window

        # Panel kapatıldığında referansı temizle
        panel_window.protocol("WM_DELETE_WINDOW",
            lambda: self.close_panel("Sakin", panel_window))

        # Panel başlığı
        header_frame = ctk.CTkFrame(panel_window, fg_color=COLORS["primary"], height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="👥 Sakin Yönetimi",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["surface"]
        )
        title_label.pack(pady=15)

        # Sakin panelini oluştur
        SakinPanel(panel_window, COLORS)

    def open_lojman_panel(self) -> None:
        """Lojman panelini aç"""
        from ui.lojman_panel import LojmanPanel

        # Eğer panel zaten açıksa, onu öne getir
        if "Lojman" in self.panels:
            panel_window = self.panels["Lojman"]
            if panel_window.winfo_exists():
                panel_window.lift()
                panel_window.focus_force()
                return

        # Yeni panel penceresi oluştur
        panel_window = ctk.CTkToplevel(self.root)
        panel_window.title(f"Aidat Plus - 🏠 Lojman Yönetimi")
        self.center_window(panel_window, 1200, 700)

        # Ana pencerenin önünde kalması için
        panel_window.transient(self.root)
        panel_window.lift()
        panel_window.focus_force()

        # Panel referansını sakla
        self.panels["Lojman"] = panel_window

        # Panel kapatıldığında referansı temizle
        panel_window.protocol("WM_DELETE_WINDOW",
            lambda: self.close_panel("Lojman", panel_window))

        # Panel başlığı
        header_frame = ctk.CTkFrame(panel_window, fg_color=COLORS["primary"], height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="🏠 Lojman Yönetimi",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["surface"]
        )
        title_label.pack(pady=15)

        # Lojman panelini oluştur
        LojmanPanel(panel_window, COLORS)

    def open_raporlar_panel(self) -> None:
        """Raporlar panelini aç"""
        from ui.raporlar_panel import RaporlarPanel

        # Eğer panel zaten açıksa, onu öne getir
        if "Raporlar" in self.panels:
            panel_window = self.panels["Raporlar"]
            if panel_window.winfo_exists():
                panel_window.lift()
                panel_window.focus_force()
                return

        # Yeni panel penceresi oluştur
        panel_window = ctk.CTkToplevel(self.root)
        panel_window.title(f"Aidat Plus - 📊 Raporlar")
        self.center_window(panel_window, 1200, 650)

        # Ana pencerenin önünde kalması için
        panel_window.transient(self.root)
        panel_window.lift()
        panel_window.focus_force()

        # Panel referansını sakla
        self.panels["Raporlar"] = panel_window

        # Panel kapatıldığında referansı temizle
        panel_window.protocol("WM_DELETE_WINDOW",
            lambda: self.close_panel("Raporlar", panel_window))

        # Panel başlığı
        header_frame = ctk.CTkFrame(panel_window, fg_color=COLORS["primary"], height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Raporlar",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["surface"]
        )
        title_label.pack(pady=15)

        # Raporlar panelini oluştur
        RaporlarPanel(panel_window, COLORS)

    def open_ayarlar_panel(self) -> None:
        """Ayarlar panelini aç"""
        from ui.ayarlar_panel import AyarlarPanel

        # Eğer panel zaten açıksa, onu öne getir
        if "Ayarlar" in self.panels:
            panel_window = self.panels["Ayarlar"]
            if panel_window.winfo_exists():
                panel_window.lift()
                panel_window.focus_force()
                return

        # Yeni panel penceresi oluştur
        panel_window = ctk.CTkToplevel(self.root)
        panel_window.title(f"Aidat Plus - ⚙️ Ayarlar")
        self.center_window(panel_window, 1200, 700)

        # Ana pencerenin önünde kalması için
        panel_window.transient(self.root)
        panel_window.lift()
        panel_window.focus_force()

        # Panel referansını sakla
        self.panels["Ayarlar"] = panel_window

        # Panel kapatıldığında referansı temizle
        panel_window.protocol("WM_DELETE_WINDOW",
            lambda: self.close_panel("Ayarlar", panel_window))

        # Panel başlığı
        header_frame = ctk.CTkFrame(panel_window, fg_color=COLORS["primary"], height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ Ayarlar",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["surface"]
        )
        title_label.pack(pady=15)

        # Ayarlar panelini oluştur
        AyarlarPanel(panel_window, COLORS)

    def open_panel(self, panel_name: str, title: str) -> None:
        """Yeni panel penceresi aç"""
        # Eğer panel zaten açıksa, onu öne getir
        if panel_name in self.panels:
            panel_window = self.panels[panel_name]
            if panel_window.winfo_exists():
                panel_window.lift()
                panel_window.focus_force()
                return

        # Yeni panel penceresi oluştur
        panel_window = ctk.CTkToplevel(self.root)
        panel_window.title(f"Aidat Plus - {title}")
        self.center_window(panel_window, 1000, 700)

        # Ana pencerenin önünde kalması için
        panel_window.transient(self.root)
        panel_window.lift()
        panel_window.focus_force()

        # Panel referansını sakla
        self.panels[panel_name] = panel_window

        # Panel kapatıldığında referansı temizle
        panel_window.protocol("WM_DELETE_WINDOW",
            lambda: self.close_panel(panel_name, panel_window))

        # Panel başlığı
        header_frame = ctk.CTkFrame(panel_window, fg_color=COLORS["primary"], height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["surface"]
        )
        title_label.pack(pady=15)

        # Ana panel içeriği
        content_frame = ctk.CTkFrame(panel_window, fg_color=COLORS["background"])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Geçici içerik
        temp_label = ctk.CTkLabel(
            content_frame,
            text=f"{panel_name} paneli yakında eklenecek...",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_secondary"]
        )
        temp_label.pack(expand=True)

    def center_window(self, window: ctk.CTkToplevel, width: int, height: int) -> None:
        """Yeni pencereyi ana pencerenin üstünden 2cm aşağıdan başlayacak şekilde konumlandır"""
        # Ana pencere konumunu ve boyutunu al
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        
        # Yeni pencerenin konumunu hesapla
        # X: ana pencerenin merkezi
        x = root_x + (root_width - width) // 2
        # Y: ana pencerenin üstünden 75 piksel (≈2cm) aşağı
        y = root_y + 75
        
        window.geometry(f"{width}x{height}+{x}+{y}")

    def close_panel(self, panel_name: str, window: ctk.CTkToplevel) -> None:
        """Paneli kapat"""
        if panel_name in self.panels:
            del self.panels[panel_name]
        window.destroy()

    def run(self) -> None:
        """Uygulamayı çalıştır"""
        self.root.mainloop()


def main() -> None:
    """Ana fonksiyon
    
    1. Configuration Manager'ı başlatır
    2. Logging'i ayarlar
    3. Veritabanı tablolarını oluşturur
    4. Uygulamayı çalıştırır
    
    Raises:
        Exception: Kritik hata durumlarında
    """
    try:
        logger.info("Veritabanı tabloları kontrol ediliyor...")
        # Veritabanı tablolarını kontrol et ve oluştur
        from database.config import Base, engine

        # Veritabanı tablolarını oluştur (varsa dokunma, yoksa oluştur)
        Base.metadata.create_all(bind=engine)
        logger.info("Veritabanı tabloları hazırlandı")

        logger.info("Uygulama penceresi oluşturuluyor...")
        app = AidatPlusApp()
        logger.info("Aidat Plus başarıyla başlatıldı")
        app.run()
        
    except Exception as e:
        logger.critical(f"Uygulama başlatılırken kritik hata: {str(e)}", exc_info=True)
        messagebox.showerror("Hata", f"Uygulama başlatılırken hata oluştu:\n{str(e)}")


if __name__ == "__main__":
    main()
