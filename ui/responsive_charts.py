"""
Responsive Grafikler - Pencere boyutuna göre dinamik grafik ölçeklendirmesi

Bu modül, matplotlib grafiklerinin pencere boyutuna göre dinamik olarak
boyutlandırılmasını ve konumlandırılmasını sağlar.
"""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Tuple, Optional, Any
import logging


class ResponsiveChartManager:
    """
    Responsive Grafik Yöneticisi.
    
    Matplotlib figürlerin pencere boyutuna göre dinamik boyutlandırılmasını sağlar.
    DPI ayarlamaları ve figsize hesaplamaları otomatik yapılır.
    """
    
    def __init__(self, container: ctk.CTkFrame) -> None:
        """
        Responsive Chart Manager'ı başlat.
        
        Args:
            container: Grafikleri içerecek container frame
        """
        self.container = container
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Container'ın boyutunu al
        self.container_width = container.winfo_width() or 800
        self.container_height = container.winfo_height() or 600
        
        # Bind'i ayarlayarak resize'ı dinle
        self.container.bind("<Configure>", self._on_container_resize)
        
        self.logger.debug(
            f"ResponsiveChartManager initialized: "
            f"{self.container_width}x{self.container_height}"
        )
    
    def _on_container_resize(self, event: Any) -> None:
        """
        Container resize event'ini işle.
        
        Args:
            event: Configure event
        """
        try:
            self.container_width = event.width
            self.container_height = event.height
            
            self.logger.debug(
                f"Container resized: {self.container_width}x{self.container_height}"
            )
        except Exception as e:
            self.logger.error(f"Container resize error: {str(e)}")
    
    def calculate_chart_figsize(
        self,
        chart_type: str = "default",
        colspan: int = 1
    ) -> Tuple[float, float]:
        """
        Grafik türüne göre responsive figsize hesapla.
        Scroll çubuğu olmayan responsive design için optimize edilmiş.
        
        Args:
            chart_type: Grafik türü ("trend", "pie", "bar", "default")
            colspan: Sütun genişliği (1 = normal, 2 = geniş)
        
        Returns:
            Tuple: (width, height) inç cinsinden
        """
        # Container genişliğine göre hesapla
        # Padding: left 10px + right 10px + inner padding 6px * 2
        effective_width = self.container_width - 32
        
        # Grafik türüne göre grid kolonu sayısı belirle
        if chart_type == "trend":
            # Trend: 2 sütun (colspan=2)
            available_width = effective_width  # Tüm genişlik
        else:
            # Pie/Bar: 1 sütun
            available_width = (effective_width - 6) / 2  # 2 sütunlu grid, ortasında 6px boşluk
        
        # Maksimum/minimum genişlik
        available_width = max(available_width, 200)
        available_width = min(available_width, 800)  # Maksimum genişlik
        
        # Inç'e dönüştür (96 DPI varsayılan)
        width_inch = available_width / 96
        
        # Grafik türüne göre boyut hesapla
        if chart_type == "trend":
            # Trend chart: Çok geniş ve dar (colspan=2)
            height_inch = 2.8
            # Genişliği optimize et
            width_inch = min(width_inch, 10)  # Maksimum 10 inç
        elif chart_type == "pie":
            # Pie chart: Kare benzeri
            size = min(width_inch, 3.2)
            height_inch = size * 0.9
            width_inch = size
        elif chart_type == "bar":
            # Bar chart: Orta yükseklik
            height_inch = 2.5
            width_inch = min(width_inch, 4.2)
        else:  # default
            # Default: Standart boyut
            height_inch = 2.2
            width_inch = min(width_inch, 4)
        
        # Minimum kontrol
        width_inch = max(width_inch, 1.5)
        height_inch = max(height_inch, 1.0)
        
        self.logger.debug(
            f"Calculated figsize for {chart_type}: "
            f"{width_inch:.2f}x{height_inch:.2f} inches"
        )
        
        return width_inch, height_inch
    
    def get_responsive_dpi(self) -> int:
        """
        Ekran çözünürlüğüne göre responsive DPI hesapla.
        
        Returns:
            int: DPI değeri (80-120 arası)
        """
        # Ekran çözünürlüğüne göre DPI ayarla
        screen_dpi = self.container.winfo_fpixels('1i')
        
        # 96 DPI'a normalize et
        dpi = min(int(screen_dpi), 120)
        dpi = max(dpi, 80)
        
        return dpi
    
    def embed_chart(
        self,
        parent: ctk.CTkFrame,
        figure: Figure,
        chart_type: str = "default",
        colspan: int = 1
    ) -> FigureCanvasTkAgg:
        """
        Matplotlib figürünü responsive olarak embed et.
        
        Args:
            parent: Grafiği içerecek parent frame
            figure: Matplotlib Figure nesnesi
            chart_type: Grafik türü
            colspan: Sütun genişliği
        
        Returns:
            FigureCanvasTkAgg: Canvas nesnesi
        """
        try:
            # Canvas oluştur
            canvas = FigureCanvasTkAgg(figure, master=parent)
            canvas.draw()
            
            # Widget'ı pack et
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill="both", expand=True, padx=3, pady=3)
            
            self.logger.debug(f"Chart embedded: {chart_type}")
            
            return canvas
        except Exception as e:
            self.logger.error(f"Chart embedding error: {str(e)}")
            raise


class ResponsiveChartBuilder:
    """
    Responsive Grafik İnşaatçısı.
    
    Responsive boyutlarla matplotlib grafikleri oluşturmayı kolaylaştırır.
    """
    
    def __init__(self, chart_manager: ResponsiveChartManager) -> None:
        """
        Chart Builder'ı başlat.
        
        Args:
            chart_manager: ResponsiveChartManager nesnesi
        """
        self.manager = chart_manager
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_responsive_line_chart(
        self,
        x_data: list,
        y_data_dict: dict,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        colors: Optional[dict] = None,
        colspan: int = 1
    ) -> Figure:
        """
        Responsive çizgi grafik oluştur.
        
        Args:
            x_data: X ekseni verileri (liste)
            y_data_dict: Y ekseni verileri dictionary ({label: [values]})
            title: Grafik başlığı
            xlabel: X ekseni etiketi
            ylabel: Y ekseni etiketi
            colors: Renk dictionary'si (label: color)
            colspan: Sütun genişliği
        
        Returns:
            Figure: Matplotlib Figure nesnesi
        """
        try:
            # Responsive boyut
            figsize = self.manager.calculate_chart_figsize("trend", colspan)
            dpi = self.manager.get_responsive_dpi()
            
            # Figure oluştur
            fig = Figure(figsize=figsize, dpi=dpi)
            ax = fig.add_subplot(111)
            
            # Verileri çiz
            x_range = range(len(x_data))
            for label, y_values in y_data_dict.items():
                color = colors.get(label, "#0055A4") if colors else "#0055A4"
                ax.plot(x_range, y_values, marker='o', label=label, 
                       color=color, linewidth=2, markersize=5)
            
            # Eksen ayarları
            ax.set_xticks(x_range)
            ax.set_xticklabels(x_data, rotation=45, ha='right', fontsize=8)
            ax.set_xlabel(xlabel, fontsize=8)
            ax.set_ylabel(ylabel, fontsize=8)
            ax.legend(loc='upper left', fontsize=7)
            ax.grid(True, alpha=0.2)
            ax.tick_params(labelsize=7)
            
            fig.tight_layout()
            
            self.logger.debug(f"Line chart created: {figsize}")
            
            return fig
        except Exception as e:
            self.logger.error(f"Line chart creation error: {str(e)}")
            raise
    
    def create_responsive_pie_chart(
        self,
        sizes: list,
        labels: list,
        colors: Optional[list] = None,
        title: str = ""
    ) -> Figure:
        """
        Responsive pasta grafik oluştur.
        
        Args:
            sizes: Pasta dilimlerinin boyutları
            labels: Etiketler
            colors: Renkler (liste)
            title: Grafik başlığı
        
        Returns:
            Figure: Matplotlib Figure nesnesi
        """
        try:
            # Responsive boyut
            figsize = self.manager.calculate_chart_figsize("pie")
            dpi = self.manager.get_responsive_dpi()
            
            # Figure oluştur
            fig = Figure(figsize=figsize, dpi=dpi)
            ax = fig.add_subplot(111)
            
            # Pasta grafik çiz
            default_colors = ['#28A745', '#0055A4', '#FFC107', '#DC3545', '#17A2B8']
            pie_colors = colors or default_colors[:len(sizes)]
            
            ax.pie(
                sizes,
                labels=labels,
                autopct='%1.0f%%',
                colors=pie_colors,
                startangle=90,
                textprops={'fontsize': 6}
            )
            
            if title:
                ax.set_title(title, fontsize=8, weight='bold')
            
            fig.tight_layout()
            
            self.logger.debug(f"Pie chart created: {figsize}")
            
            return fig
        except Exception as e:
            self.logger.error(f"Pie chart creation error: {str(e)}")
            raise
    
    def create_responsive_bar_chart(
        self,
        x_data: list,
        y_data: list,
        colors: Optional[list] = None,
        title: str = "",
        xlabel: str = "",
        ylabel: str = ""
    ) -> Figure:
        """
        Responsive bar grafik oluştur.
        
        Args:
            x_data: X ekseni verileri
            y_data: Y ekseni verileri
            colors: Bar renkleri
            title: Grafik başlığı
            xlabel: X ekseni etiketi
            ylabel: Y ekseni etiketi
        
        Returns:
            Figure: Matplotlib Figure nesnesi
        """
        try:
            # Responsive boyut
            figsize = self.manager.calculate_chart_figsize("bar")
            dpi = self.manager.get_responsive_dpi()
            
            # Figure oluştur
            fig = Figure(figsize=figsize, dpi=dpi)
            ax = fig.add_subplot(111)
            
            # Bar grafik çiz
            bar_colors = colors or ['#0055A4'] * len(x_data)
            ax.bar(range(len(x_data)), y_data, color=bar_colors, alpha=0.8)
            
            # Eksen ayarları
            ax.set_xticks(range(len(x_data)))
            ax.set_xticklabels(x_data, rotation=45, ha='right', fontsize=8)
            ax.set_xlabel(xlabel, fontsize=8)
            ax.set_ylabel(ylabel, fontsize=8)
            
            if title:
                ax.set_title(title, fontsize=9, weight='bold')
            
            ax.grid(True, alpha=0.2, axis='y')
            ax.tick_params(labelsize=7)
            
            fig.tight_layout()
            
            self.logger.debug(f"Bar chart created: {figsize}")
            
            return fig
        except Exception as e:
            self.logger.error(f"Bar chart creation error: {str(e)}")
            raise


def create_responsive_figure(
    chart_type: str = "line",
    container_width: int = 800,
    container_height: int = 600,
    colspan: int = 1
) -> Tuple[Figure, int]:
    """
    Responsive matplotlib figure oluşturma yardımcı fonksiyonu.
    
    Args:
        chart_type: Grafik türü ("line", "pie", "bar", "default")
        container_width: Container genişliği (piksel)
        container_height: Container yüksekliği (piksel)
        colspan: Sütun genişliği
    
    Returns:
        Tuple: (Figure, DPI)
    """
    # Responsive boyut hesapla
    effective_width = container_width - (20 + 6 * colspan)
    effective_width = min(max(effective_width, 200), 1000)
    width_inch = effective_width / 96
    
    # Grafik türüne göre boyut
    if chart_type == "line":
        height_inch = 2.8
        width_inch = (width_inch * 2) - 0.5 if colspan > 1 else width_inch
    elif chart_type == "pie":
        size = min(width_inch * 0.8, 3.5)
        width_inch = size
        height_inch = size * 0.9
    elif chart_type == "bar":
        height_inch = 2.5
        width_inch = min(width_inch, 4.5)
    else:
        height_inch = 2.2
        width_inch = min(width_inch, 4)
    
    # DPI hesapla
    dpi = min(int(96), 120)  # 96-120 arası
    
    return Figure(figsize=(width_inch, height_inch), dpi=dpi), dpi
