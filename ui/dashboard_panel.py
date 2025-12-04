"""
Dashboard paneli - Ana sayfa için istatistikler ve grafikler
"""

import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from ui.base_panel import BasePanel
from ui.responsive_charts import ResponsiveChartManager, ResponsiveChartBuilder
from typing import Optional
from ui.error_handler import (
    ErrorHandler, handle_exception, show_error, show_success, show_warning
)
from controllers.hesap_controller import HesapController
from controllers.finans_islem_controller import FinansIslemController
from controllers.sakin_controller import SakinController
from controllers.aidat_controller import AidatIslemController
from controllers.daire_controller import DaireController
from models.base import FinansIslem, Hesap
from models.exceptions import DatabaseError
from database.config import get_db
from sqlalchemy import and_


class DashboardPanel(BasePanel):
    """Dashboard/Ana sayfa paneli
    
    KPI kartları, finansal analizler ve grafiklerle ana özet görünümü sağlar.
    
    Attributes:
        hesap_controller (HesapController): Hesap yönetim denetleyicisi
        finans_controller (FinansIslemController): Finansal işlem denetleyicisi
        sakin_controller (SakinController): Sakin yönetim denetleyicisi
        aidat_controller (AidatIslemController): Aidat yönetim denetleyicisi
        daire_controller (DaireController): Daire yönetim denetleyicisi
        colors (dict): Renk şeması
        refresh_interval (int): Otomatik yenileme aralığı (milisaniye)
        refresh_job: Otomatik yenileme işi referansı
        scroll_frame (ctk.CTkScrollableFrame): Ana kaydırılabilir çerçeve
    """

    def __init__(self, parent: ctk.CTk, colors: dict) -> None:
        self.hesap_controller = HesapController()
        self.finans_controller = FinansIslemController()
        self.sakin_controller = SakinController()
        self.aidat_controller = AidatIslemController()
        self.daire_controller = DaireController()
        self.colors = colors
        self.refresh_interval = 300000  # 5 dakika (milisaniye cinsinden)
        self.refresh_job = None
        self.last_update_label: Optional[ctk.CTkLabel] = None
        self.chart_manager: Optional[ResponsiveChartManager] = None
        self.chart_builder: Optional[ResponsiveChartBuilder] = None
        
        # Önceki pencere boyutunu sakla (pencere resize'ında overkill refresh'i önle)
        self._last_window_width = 0
        self._last_window_height = 0
        
        super().__init__(parent, "📊 Dashboard", colors)

    def load_data(self) -> None:
        """Verileri yükle
        
        Başlangıç verilerini yüklemek için kullanılan metod.
        """
        pass
    
    def _get_formatted_time(self) -> str:
        """Son güncelleme saatini formatlı göster
        
        Returns:
            str: Güncellenme saatinin formatlanmış metni
        """
        now = datetime.now()
        return now.strftime("Güncelleme: %d.%m.%Y %H:%M:%S")
    
    def refresh_dashboard(self) -> None:
        """Dashboard'u yenile - tüm bileşenleri temizle ve yeniden oluştur
        
        KPI kartlarını ve grafikleri temizleyip yeniden oluşturur.
        """
        # Önceki bileşenleri temizle
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # ===== KPI CARDS BÖLÜMÜ =====
        self.setup_kpi_cards(self.scroll_frame)
        
        # Son güncelleme saatini güncelle
        if self.last_update_label is not None:
            self.last_update_label.configure(text=self._get_formatted_time())

        # Divider
        divider = ctk.CTkFrame(self.scroll_frame, fg_color=self.colors["border"], height=1)
        divider.pack(fill="x", pady=(3, 5))

        # ===== GRAFIKLER BÖLÜMÜ =====
        self.setup_charts(self.scroll_frame)
    
    def start_auto_refresh(self) -> None:
        """Otomatik yenileme başlat
        
        Dashboard'u belirli aralıklarla yenilemek için periyodik görev başlatır.
        5 dakikada bir otomatik yenilenir.
        """
        # Önceki görev varsa iptal et
        if self.refresh_job:
            self.frame.after_cancel(self.refresh_job)
        
        # Dashboard'u yenile
        self.refresh_dashboard()
        
        # Sonraki yenilemeyi planla
        self.refresh_job = self.frame.after(self.refresh_interval, self.start_auto_refresh)
    
    def stop_auto_refresh(self) -> None:
        """Otomatik yenilemeyi durdur
        
        Periyodik dashboard yenileme görevini iptal eder.
        """
        if self.refresh_job:
            self.frame.after_cancel(self.refresh_job)
            self.refresh_job = None

    def setup_ui(self) -> None:
        """UI'yi oluştur
        
        Dashboard ana arayüzünü başlatır ve otomatik yenilemeyi başlatır.
        Scroll çubuğu olmadan responsive frame'lerle otomatik boyutlandırma.
        """
        # Ana container - responsive frame (scroll yok!)
        main_frame = ctk.CTkFrame(self.frame, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Content frame - responsive (scroll frame değil)
        self.scroll_frame = main_frame
        
        # Responsive chart manager'ı başlat
        self.chart_manager = ResponsiveChartManager(self.scroll_frame)
        self.chart_builder = ResponsiveChartBuilder(self.chart_manager)

        # ===== KPI CARDS BÖLÜMÜ =====
        self.kpi_frame = None
        self.charts_grid = None
        self.refresh_dashboard()
        
        # Otomatik yenileme başlat
        self.start_auto_refresh()

    def setup_kpi_cards(self, parent: ctk.CTkFrame) -> None:
        """KPI kartlarını oluştur
        
        6 temel KPI kartı (Bakiye, Gelir, Gider, Net, Lojmanlar, Tahsilat) oluşturur.
        Grid layout kullanarak responsive yerleştirme.
        
        Args:
            parent (ctk.CTkFrame): Kartları içerecek ana çerçeve
        """
        cards_frame = ctk.CTkFrame(parent, fg_color=self.colors["background"])
        cards_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Başlık ve son güncelleme saati
        title_frame = ctk.CTkFrame(cards_frame, fg_color=self.colors["background"])
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Özet İstatistikler",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(anchor="w", side="left")
        
        # Son güncelleme saati ve yenile butonu (sağ tarafta)
        refresh_frame = ctk.CTkFrame(title_frame, fg_color=self.colors["background"])
        refresh_frame.pack(anchor="e", side="right")
        
        self.last_update_label = ctk.CTkLabel(
            refresh_frame,
            text=self._get_formatted_time(),
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text_secondary"]
        )
        self.last_update_label.pack(side="left", padx=(0, 10))
        
        # Yenile ikonu (buton)
        refresh_btn = ctk.CTkButton(
            refresh_frame,
            text="🔄",
            command=self.refresh_dashboard,
            fg_color="transparent",
            hover_color=self.colors["text_secondary"],
            text_color="#4a4a4a",
            font=ctk.CTkFont(size=18),
            width=40,
            height=30
        )
        refresh_btn.pack(side="left")

        # KPI grid - Grid layout ile responsive yerleştirme
        kpi_grid = ctk.CTkFrame(cards_frame, fg_color=self.colors["background"])
        kpi_grid.pack(fill="both", expand=False)

        # KPI 1: Toplam Hesap Bakiyesi
        try:
            toplam_bakiye = self.get_toplam_bakiye()
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Toplam bakiye alınırken hata: {e}")
            toplam_bakiye = 0.0
        self.create_kpi_card(
            kpi_grid, 
            "💰 Toplam Bakiye", 
            f"₺{toplam_bakiye:,.2f}",
            self.colors["success"],
            0
        )

        # KPI 2: Bu Ay Gelirleri
        try:
            bu_ay_geliri = self.get_bu_ay_geliri()
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Bu ay geliri alınırken hata: {e}")
            bu_ay_geliri = 0.0
        self.create_kpi_card(
            kpi_grid,
            "📈 Bu Ay Gelirleri",
            f"₺{bu_ay_geliri:,.2f}",
            self.colors["primary"],
            1
        )

        # KPI 3: Bu Ay Giderleri
        try:
            bu_ay_gideri = self.get_bu_ay_gideri()
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Bu ay gideri alınırken hata: {e}")
            bu_ay_gideri = 0.0
        self.create_kpi_card(
            kpi_grid,
            "📉 Bu Ay Giderleri",
            f"₺{bu_ay_gideri:,.2f}",
            self.colors["error"],
            2
        )

        # KPI 4: Net Durum
        try:
            net_durum = bu_ay_geliri - bu_ay_gideri
            renk = self.colors["success"] if net_durum >= 0 else self.colors["error"]
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Net durum hesaplanırken hata: {e}")
            net_durum = 0.0
            renk = self.colors["error"]
        self.create_kpi_card(
            kpi_grid,
            "⚖️ Aylık Net Durum",
            f"₺{net_durum:,.2f}",
            renk,
            3
        )

        # KPI 5: Dolu Lojmanlar
        try:
            dolu_lojman = self.get_dolu_lojman_sayisi()
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Dolu lojman sayısı alınırken hata: {e}")
            dolu_lojman = 0
        self.create_kpi_card(
            kpi_grid,
            "🏘️ Dolu Lojmanlar",
            str(dolu_lojman),
            self.colors["secondary"],
            4
        )

        # KPI 6: Aidat Tahsilatı
        try:
            aidat_tahsilat = self.get_aidat_tahsilat_orani()
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Aidat tahsilat oranı alınırken hata: {e}")
            aidat_tahsilat = 0.0
        self.create_kpi_card(
            kpi_grid,
            "💳 Aidat Tahsilatı",
            f"%{aidat_tahsilat:.1f}",
            self.colors["warning"],
            5
        )

    def create_kpi_card(self, parent: ctk.CTkFrame, title: str, value: str, accent_color: str, column: int) -> None:
        """KPI kartı oluştur
        
        Belirtilen başlık ve değerle görsel KPI kartı oluşturur.
        
        Args:
            parent (ctk.CTkFrame): Kartın ekleneceği çerçeve
            title (str): Kart başlığı
            value (str): Kart değeri (sayı, yüzde, vb.)
            accent_color (str): Kartın vurgu rengi (hex)
            column (int): Grid kolon indeksi
        """
        card = ctk.CTkFrame(parent, fg_color=self.colors["surface"], corner_radius=6, height=55)
        card.grid(row=0, column=column, padx=4, pady=3, sticky="ew")
        card.pack_propagate(False)
        parent.grid_columnconfigure(column, weight=1)

        # Sol şerit (renk)
        strip = ctk.CTkFrame(card, fg_color=accent_color, width=3)
        strip.pack(side="left", fill="y", padx=0)

        # İçerik
        content = ctk.CTkFrame(card, fg_color=self.colors["surface"])
        content.pack(fill="both", expand=True, padx=8, pady=5)

        # Başlık
        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text_secondary"]
        )
        title_label.pack(anchor="w")

        # Değer
        value_label = ctk.CTkLabel(
            content,
            text=value,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=accent_color
        )
        value_label.pack(anchor="w", pady=(1, 0))

    def setup_charts(self, parent: ctk.CTkFrame) -> None:
        """Grafikleri oluştur
        
        3 temel grafik (Trend, Bakiye Dağılımı, Aidat Durum) oluşturur.
        Grid layout ile responsive yerleştirme, scroll çubuğu yok.
        
        Args:
            parent (ctk.CTkFrame): Grafikleri içerecek ana çerçeve
        """
        charts_frame = ctk.CTkFrame(parent, fg_color=self.colors["background"])
        charts_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Başlık
        title_label = ctk.CTkLabel(
            charts_frame,
            text="Finansal Analizler",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(anchor="w", pady=(0, 10))

        # Grafikleri içeren grid - Responsive grid layout
        charts_grid = ctk.CTkFrame(charts_frame, fg_color=self.colors["background"])
        charts_grid.pack(fill="both", expand=True)
        
        # Grid satırlarının eşit boyut almasını sağla (pack'den sonra)
        charts_grid.grid_rowconfigure(0, weight=1)
        charts_grid.grid_rowconfigure(1, weight=1)
        charts_grid.grid_columnconfigure(0, weight=1)
        charts_grid.grid_columnconfigure(1, weight=1)

        # 1. Son 6 ay gelir/gider trendi (geniş, 2 sütun)
        self.create_trend_chart(charts_grid, 0, 0, colspan=2)

        # 2. Hesaplar arası bakiye dağılımı
        self.create_hesap_dagitimi_chart(charts_grid, 1, 0)

        # 3. Aidat durum
        self.create_aidat_durum_chart(charts_grid, 1, 1)

    def create_trend_chart(self, parent: ctk.CTkFrame, row: int, col: int, colspan: int = 1) -> None:
        """6 aylık gelir/gider trendi
        
        Son 12 ayın gelir ve gider trendini çizgi grafik olarak gösterir.
        Responsive boyutlandırma ile ekrana göre dinamik boyut ayarlanır.
        
        Args:
            parent (ctk.CTkFrame): Grafiğin ekleneceği çerçeve
            row (int): Grid satır indeksi
            col (int): Grid kolon indeksi
            colspan (int): Sütun genişliği (varsayılan: 1)
        """
        chart_frame = ctk.CTkFrame(parent, fg_color=self.colors["surface"], corner_radius=6)
        chart_frame.grid(row=row, column=col, columnspan=colspan, padx=0, pady=3, sticky="nsew")
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        if colspan > 1:
            parent.grid_columnconfigure(col + 1, weight=1)
        
        # Başlık
        title = ctk.CTkLabel(
            chart_frame,
            text="Son 12 Ay Gelir/Gider Trendi",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors["primary"]
        )
        title.pack(anchor="w", padx=6, pady=(5, 2))
        
        # Veriler
        aylar, gelirler, giderler = self.get_6ay_trend_data()
        
        # Responsive grafik oluştur
        try:
            if self.chart_builder and self.chart_manager:
                fig = self.chart_builder.create_responsive_line_chart(
                    x_data=aylar,
                    y_data_dict={
                        'Gelirler': gelirler,
                        'Giderler': giderler
                    },
                    xlabel="",
                    ylabel='Miktar (₺)',
                    colors={'Gelirler': '#28A745', 'Giderler': '#DC3545'},
                    colspan=colspan
                )
                
                # Arka plan rengi ayarla
                for ax in fig.get_axes():
                    ax.set_facecolor(self.colors["surface"])
                fig.patch.set_facecolor(self.colors["surface"])
                
                # Canvas'ı embed et
                self.chart_manager.embed_chart(chart_frame, fig, "trend", colspan)
        except Exception as e:
            self.logger.error(f"Trend chart creation error: {str(e)}")
            error_label = ctk.CTkLabel(
                chart_frame,
                text=f"Grafik oluşturma hatası: {str(e)[:50]}",
                text_color=self.colors["error"],
                font=ctk.CTkFont(size=8)
            )
            error_label.pack(expand=True)

    def create_hesap_dagitimi_chart(self, parent: ctk.CTkFrame, row: int, col: int) -> None:
        """Hesaplar arası bakiye dağılımı
        
        Tüm hesapların bakiye dağılımını pasta grafik olarak gösterir.
        Responsive boyutlandırma ile ekrana göre dinamik boyut ayarlanır.
        
        Args:
            parent (ctk.CTkFrame): Grafiğin ekleneceği çerçeve
            row (int): Grid satır indeksi
            col (int): Grid kolon indeksi
        """
        chart_frame = ctk.CTkFrame(parent, fg_color=self.colors["surface"], corner_radius=6)
        chart_frame.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Başlık
        title = ctk.CTkLabel(
            chart_frame,
            text="Hesaplar Arası Bakiye Dağılımı",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors["primary"]
        )
        title.pack(anchor="w", padx=6, pady=(5, 2))

        # Veriler
        hesap_adlari, bakiyeler = self.get_hesap_dagitimi_data()

        if not hesap_adlari:
            info_label = ctk.CTkLabel(
                chart_frame,
                text="Henüz hesap eklenmemiş",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=8)
            )
            info_label.pack(expand=True)
            return

        # Responsive grafik oluştur
        try:
            if self.chart_builder and self.chart_manager:
                colors_list = ['#28A745', '#0055A4', '#FFC107', '#DC3545', '#17A2B8']
                fig = self.chart_builder.create_responsive_pie_chart(
                    sizes=bakiyeler,
                    labels=hesap_adlari,
                    colors=colors_list[:len(hesap_adlari)]
                )
                
                # Arka plan rengi ayarla
                for ax in fig.get_axes():
                    ax.set_facecolor(self.colors["surface"])
                fig.patch.set_facecolor(self.colors["surface"])
                
                # Canvas'ı embed et
                self.chart_manager.embed_chart(chart_frame, fig, "pie")
        except Exception as e:
            self.logger.error(f"Hesap dağılımı chart error: {str(e)}")
            error_label = ctk.CTkLabel(
                chart_frame,
                text=f"Grafik oluşturma hatası",
                text_color=self.colors["error"],
                font=ctk.CTkFont(size=8)
            )
            error_label.pack(expand=True)

    def create_aidat_durum_chart(self, parent: ctk.CTkFrame, row: int, col: int) -> None:
        """Aidat ödeme durumu
        
        Son ay aidat ödemelerinin durum dağılımını pasta grafik olarak gösterir.
        Responsive boyutlandırma ile ekrana göre dinamik boyut ayarlanır.
        
        Args:
            parent (ctk.CTkFrame): Grafiğin ekleneceği çerçeve
            row (int): Grid satır indeksi
            col (int): Grid kolon indeksi
        """
        chart_frame = ctk.CTkFrame(parent, fg_color=self.colors["surface"], corner_radius=6)
        chart_frame.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Başlık
        title = ctk.CTkLabel(
            chart_frame,
            text="Aidat Ödeme Durumu (Son Ay)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors["primary"]
        )
        title.pack(anchor="w", padx=6, pady=(5, 2))

        # Veriler
        odenen, odenmeyen = self.get_aidat_durum_data()

        # Hiç veri yoksa mesaj göster
        if odenen == 0 and odenmeyen == 0:
            info_label = ctk.CTkLabel(
                chart_frame,
                text="Henüz aidat kaydı yok",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=8)
            )
            info_label.pack(expand=True)
            return

        # Responsive grafik oluştur
        try:
            if self.chart_builder and self.chart_manager:
                labels = ['Ödenen', 'Ödenmemiş']
                sizes = [odenen, odenmeyen]
                colors_list = ['#28A745', '#DC3545']
                
                fig = self.chart_builder.create_responsive_pie_chart(
                    sizes=sizes,
                    labels=labels,
                    colors=colors_list
                )
                
                # Arka plan rengi ayarla
                for ax in fig.get_axes():
                    ax.set_facecolor(self.colors["surface"])
                fig.patch.set_facecolor(self.colors["surface"])
                
                # Canvas'ı embed et
                self.chart_manager.embed_chart(chart_frame, fig, "pie")
        except Exception as e:
            self.logger.error(f"Aidat durum chart error: {str(e)}")
            error_label = ctk.CTkLabel(
                chart_frame,
                text=f"Grafik oluşturma hatası",
                text_color=self.colors["error"],
                font=ctk.CTkFont(size=8)
            )
            error_label.pack(expand=True)

    # ===== VERİ ALMA FONKSİYONLARI =====

    def get_toplam_bakiye(self) -> float:
        """Tüm hesapların toplam bakiyesi
        
        Returns:
            float: Tüm aktif hesapların toplam bakiyesi
        """
        try:
            hesaplar = self.hesap_controller.get_aktif_hesaplar()
            return float(sum(h.bakiye for h in hesaplar)) if hesaplar else 0.0
        except Exception as e:
            self.logger.error(f"Toplam bakiye hatası: {e}")
            return 0.0

    def get_bu_ay_geliri(self) -> float:
        """Bu ay gelirleri
        
        Returns:
            float: Cari ayın toplam gelirleri
        """
        try:
            islemler = self.finans_controller.get_gelirler()
            if not islemler:
                return 0.0
            
            bugun = datetime.now()
            baslangic = datetime(bugun.year, bugun.month, 1)
            
            # Bu ay'ın gelirlerini filtrele
            bu_ay_islemler = [i for i in islemler if i.tarih >= baslangic and i.tarih <= bugun]
            return float(sum(i.tutar for i in bu_ay_islemler))
        except Exception as e:
            self.logger.error(f"Gelir hesaplama hatası: {e}")
            return 0.0

    def get_bu_ay_gideri(self) -> float:
        """Bu ay giderleri
        
        Returns:
            float: Cari ayın toplam giderleri
        """
        try:
            islemler = self.finans_controller.get_giderler()
            if not islemler:
                return 0.0
            
            bugun = datetime.now()
            baslangic = datetime(bugun.year, bugun.month, 1)
            
            # Bu ay'ın giderlerini filtrele
            bu_ay_islemler = [i for i in islemler if i.tarih >= baslangic and i.tarih <= bugun]
            return float(sum(i.tutar for i in bu_ay_islemler))
        except Exception as e:
            self.logger.error(f"Gider hesaplama hatası: {e}")
            return 0.0

    def get_dolu_lojman_sayisi(self) -> int:
        """Dolu lojmanların sayısı (sakini olan daireler)
        
        Returns:
            int: Sakin barındıran daire sayısı
        """
        try:
            dolu_daireler = self.daire_controller.get_dolu_daireler()
            return len(dolu_daireler) if dolu_daireler else 0
        except Exception as e:
            self.logger.error(f"Dolu lojman sayısı hatası: {e}")
            return 0

    def get_aidat_tahsilat_orani(self) -> float:
        """Toplam aidat tahsilat oranı - tüm aidatlar bazında hesapla
        
        Returns:
            float: Aidat tahsilat yüzdesi (0-100)
        """
        try:
            # Tüm aktif aidatları getir
            db = get_db()
            try:
                from models.base import AidatIslem
                aidatlar = db.query(AidatIslem).filter(
                    AidatIslem.aktif == True
                ).options(
                    __import__('sqlalchemy.orm', fromlist=['joinedload']).joinedload(AidatIslem.odemeler)
                ).all()
            finally:
                db.close()
            
            if not aidatlar:
                return 0.0
            
            # Toplam aidat tutarı
            toplam_aidat = sum(a.toplam_tutar for a in aidatlar)
            if toplam_aidat == 0:
                return 0.0
            
            # Ödenen toplam tutar
            odenen_tutar = 0.0
            for aidat in aidatlar:
                if aidat.odemeler:
                    # Ödemeler içinde odendi=True olanların toplamı
                    ödenen = sum(o.tutar for o in aidat.odemeler if o.odendi)
                    odenen_tutar += float(ödenen)
            
            # Yüzde hesapla
            oran = (odenen_tutar / float(toplam_aidat)) * 100.0
            return float(min(oran, 100.0))  # 100'den fazla olmasın
        except Exception as e:
            self.logger.error(f"Toplam aidat tahsilat oranı hatası: {e}")
            return 0.0

    def get_6ay_trend_data(self) -> tuple[list[str], list[float], list[float]]:
        """Son 12 aylık gelir/gider trendi
        
        Returns:
            tuple: (ay_kısaltmaları, gelirler, giderler) listelerinin tuple'ı
        """
        aylar = []
        gelirler = []
        giderler = []
        
        # Türkçe ay kısaltmaları
        tr_aylar = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
        
        try:
            all_gelirler = self.finans_controller.get_gelirler() or []
            all_giderler = self.finans_controller.get_giderler() or []
            
            for i in range(11, -1, -1):
                tarih = datetime.now() - timedelta(days=30*i)
                ay_baslangic = datetime(tarih.year, tarih.month, 1)
                
                # Sonraki ayın ilk günü
                if tarih.month == 12:
                    ay_sonu = datetime(tarih.year + 1, 1, 1)
                else:
                    ay_sonu = datetime(tarih.year, tarih.month + 1, 1)
                
                # Bu aydaki işlemleri filtrele
                ay_gelir_list = [g for g in all_gelirler if g.tarih >= ay_baslangic and g.tarih <= ay_sonu]
                ay_gider_list = [g for g in all_giderler if g.tarih >= ay_baslangic and g.tarih <= ay_sonu]
                
                ay_gelir = sum(i.tutar for i in ay_gelir_list)
                ay_gider = sum(i.tutar for i in ay_gider_list)
                
                # Türkçe ay kısaltması kullan
                aylar.append(tr_aylar[tarih.month - 1])
                gelirler.append(ay_gelir)
                giderler.append(ay_gider)
        except Exception as e:
            print(f"Trend veri hatası: {e}")
            pass
        
        return aylar or ["Veri Yok"], gelirler or [0.0], giderler or [0.0]

    def get_hesap_dagitimi_data(self) -> tuple[list[str], list[float]]:
        """Hesaplar arası bakiye dağılımı
        
        Returns:
            tuple: (hesap_adları, bakiyeler) listelerinin tuple'ı
        """
        hesap_adlari = []
        bakiyeler = []
        
        try:
            hesaplar = self.hesap_controller.get_aktif_hesaplar()
            if hesaplar:
                for h in hesaplar:
                    if h.bakiye > 0:
                        hesap_adlari.append(h.ad)
                        bakiyeler.append(h.bakiye)
        except Exception as e:
            print(f"Hesap dağılımı hatası: {e}")
            pass
        
        return hesap_adlari, bakiyeler

    def get_aidat_durum_data(self) -> tuple[float, float]:
        """Bu ay aidat ödeme durumu (tutar bazında) - grafik için
        
        Returns:
            tuple: (ödenen_tutar, ödenmemiş_tutar)
        """
        odenen_tutar = 0
        odenmeyen_tutar = 0
        
        try:
            bugun = datetime.now()
            aidatlar = self.aidat_controller.get_by_yil_ay(bugun.year, bugun.month)
            
            if aidatlar:
                for aidat in aidatlar:
                    if aidat.odemeler:
                        toplam_odenen = sum(o.tutar for o in aidat.odemeler if o.odendi)
                        ödenen = toplam_odenen
                        ödenmemiş = aidat.toplam_tutar - toplam_odenen
                    else:
                        ödenen = 0
                        ödenmemiş = aidat.toplam_tutar
                    
                    odenen_tutar += ödenen
                    odenmeyen_tutar += ödenmemiş
        except Exception as e:
            print(f"Aidat durum hatası: {e}")
            pass
        
        return odenen_tutar, odenmeyen_tutar


