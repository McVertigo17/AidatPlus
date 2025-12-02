"""
Responsive UI Modülü - Ekran boyutuna göre dinamik pencere yönetimi

Bu modül, CustomTkinter uygulamalarında responsive tasarımı sağlar.
Pencere boyutlandırması, frame konumlandırması ve scroll mekanizmaları
ekran boyutuna ve içerik boyutuna göre dinamik olarak ayarlanır.
"""

import customtkinter as ctk
from tkinter import Canvas
from typing import Optional, Callable, Any, Dict, Tuple
import logging


class ResponsiveFrame(ctk.CTkFrame):
    """
    Responsive özellikleri olan Frame sınıfı.
    
    Ekran boyutuna göre otomatik olarak boyut ve pozisyon ayarlar.
    İçerik dolduğunda scrollable olabilir.
    """
    
    def __init__(
        self,
        parent: Any,
        fg_color: str = "transparent",
        min_width: int = 200,
        min_height: int = 200,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        """
        Responsive Frame'i başlat.
        
        Args:
            parent: Parent widget
            fg_color: Frame arka plan rengi
            min_width: Minimum genişlik (piksel)
            min_height: Minimum yükseklik (piksel)
            max_width: Maksimum genişlik (piksel, None=sınırsız)
            max_height: Maksimum yükseklik (piksel, None=sınırsız)
            **kwargs: Diğer CTkFrame parametreleri
        """
        super().__init__(parent, fg_color=fg_color, **kwargs)
        
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Bind'i ayarlayarak pencere resize'ını dinle
        self.bind("<Configure>", self._on_resize)
    
    def _on_resize(self, event: Any) -> None:
        """
        Resize event'ini işle.
        
        Args:
            event: Configure event
        """
        try:
            width = max(self.min_width, event.width)
            if self.max_width:
                width = min(width, self.max_width)
            
            height = max(self.min_height, event.height)
            if self.max_height:
                height = min(height, self.max_height)
            
            # Log'a kaydet
            self.logger.debug(f"Frame resize: {width}x{height}")
        except Exception as e:
            self.logger.error(f"Resize event error: {str(e)}")


class ScrollableFrame(ctk.CTkScrollableFrame):
    """
    Scrollable Frame - İçerik dolduğunda scroll çubukları otomatik çıkar.
    
    CustomTkinter'ın varsayılan ScrollableFrame'ine ek özellikler ekler.
    """
    
    def __init__(
        self,
        parent: Any,
        fg_color: str = "transparent",
        scrollbar_width: int = 12,
        **kwargs: Any
    ) -> None:
        """
        Scrollable Frame'i başlat.
        
        Args:
            parent: Parent widget
            fg_color: Frame arka plan rengi
            scrollbar_width: Scroll çubuğu genişliği (piksel)
            **kwargs: Diğer CTkScrollableFrame parametreleri
        """
        super().__init__(
            parent,
            fg_color=fg_color,
            scrollbar_width=scrollbar_width,
            **kwargs
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def reset_scrollbar(self) -> None:
        """Scroll çubuğunu sıfırla (en üste kaydır)"""
        try:
            self._parent_canvas.yview_moveto(0)
            self.logger.debug("Scrollbar reset to top")
        except Exception as e:
            self.logger.warning(f"Reset scrollbar error: {str(e)}")
    
    def scroll_to_widget(self, widget: ctk.CTkBaseClass) -> None:
        """
        Belirli bir widget'a scroll et.
        
        Args:
            widget: Scroll edilecek widget
        """
        try:
            # Widget'ın Y koordinatını al
            widget_y = widget.winfo_y()
            
            # Canvas'ın boyutunu al
            canvas_height = self._parent_canvas.winfo_height()
            
            # Scroll pozisyonunu hesapla (widget'ı ortalı olarak göster)
            scroll_position = max(0, widget_y - canvas_height // 2)
            
            # Normalize et (0.0 - 1.0 arası)
            max_scroll = self._parent_canvas.bbox("all")[3]
            if max_scroll > 0:
                normalized_position = scroll_position / max_scroll
                self._parent_canvas.yview_moveto(normalized_position)
                self.logger.debug(f"Scrolled to widget: {widget}")
        except Exception as e:
            self.logger.warning(f"Scroll to widget error: {str(e)}")


class ResponsiveWindow:
    """
    Responsive Pencere Yöneticisi.
    
    Pencere boyutlandırması, konumlandırması ve ekran uyumluluğunu yönetir.
    Minimum/maksimum boyut kısıtlamaları, ekran ortala, vs.
    """
    
    def __init__(self, window: ctk.CTk) -> None:
        """
        Responsive Window'u başlat.
        
        Args:
            window: CTk ana penceresi
        """
        self.window = window
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ekran bilgilerini al
        self.screen_width = window.winfo_screenwidth()
        self.screen_height = window.winfo_screenheight()
        
        # Varsayılan minimum/maksimum boyutlar
        self.min_window_width = 800
        self.min_window_height = 600
        self.max_window_width = self.screen_width
        self.max_window_height = self.screen_height - 100  # Taskbar'a yer bırak
        
        # Bind'i ayarlayarak resize'ı dinle
        self.window.bind("<Configure>", self._on_window_resize)
        
        self.logger.debug(
            f"ResponsiveWindow initialized: "
            f"Screen {self.screen_width}x{self.screen_height}"
        )
    
    def set_window_size_constraints(
        self,
        min_width: int = 800,
        min_height: int = 600,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ) -> None:
        """
        Pencere boyutu kısıtlamalarını ayarla.
        
        Args:
            min_width: Minimum genişlik (piksel)
            min_height: Minimum yükseklik (piksel)
            max_width: Maksimum genişlik (piksel, None=ekran genişliği)
            max_height: Maksimum yükseklik (piksel, None=ekran yüksekliği)
        """
        self.min_window_width = min_width
        self.min_window_height = min_height
        self.max_window_width = max_width or self.screen_width
        self.max_window_height = max_height or (self.screen_height - 100)
        
        # minsize() ve maxsize() kullanarak kısıtlamaları uygula
        self.window.minsize(self.min_window_width, self.min_window_height)
        self.window.maxsize(self.max_window_width, self.max_window_height)
        
        self.logger.debug(
            f"Window size constraints: "
            f"{self.min_window_width}x{self.min_window_height} ~ "
            f"{self.max_window_width}x{self.max_window_height}"
        )
    
    def center_window(self, width: int, height: int) -> None:
        """
        Pencereyi ekrana ortala.
        
        Args:
            width: Pencere genişliği (piksel)
            height: Pencere yüksekliği (piksel)
        """
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.logger.debug(f"Window centered: {width}x{height}+{x}+{y}")
    
    def center_relative_to_parent(
        self,
        child_window: ctk.CTkToplevel,
        width: int,
        height: int,
        offset_y: int = 75
    ) -> None:
        """
        Alt pencereyi ana pencereye göre ortala.
        
        Args:
            child_window: Alt penceresi (CTkToplevel)
            width: Pencere genişliği (piksel)
            height: Pencere yüksekliği (piksel)
            offset_y: Ana pencereden dikey offset (piksel, default: 75)
        """
        try:
            # Ana pencere konumunu al
            root_x = self.window.winfo_x()
            root_y = self.window.winfo_y()
            root_width = self.window.winfo_width()
            
            # Alt pencerenin konumunu hesapla
            x = root_x + (root_width - width) // 2
            y = root_y + offset_y
            
            child_window.geometry(f"{width}x{height}+{x}+{y}")
            self.logger.debug(
                f"Child window positioned: {width}x{height}+{x}+{y}"
            )
        except Exception as e:
            self.logger.warning(
                f"Error centering child window: {str(e)}"
            )
    
    def _on_window_resize(self, event: Any) -> None:
        """
        Pencere resize event'ini işle.
        
        Args:
            event: Configure event
        """
        try:
            # Pencere resize sırasında boyut sıkıştırılmasını devre dışı bırak
            # Kullanıcı istediği boyuta pencereyi açıp kapatabilir
            self.logger.debug(f"Window resized: {event.width}x{event.height}")
        except Exception as e:
            self.logger.error(f"Window resize error: {str(e)}")
    
    def is_fullscreen(self) -> bool:
        """
        Pencere tamamen ekran boyutunda mı kontrol et.
        
        Returns:
            True eğer pencere fulll ekran boyutundaysa
        """
        geometry = self.window.geometry()
        width_height = geometry.split("+")[0]
        width, height = map(int, width_height.split("x"))
        
        # Biraz hata payı (10 piksel)
        is_fs: bool = (
            abs(width - self.max_window_width) < 10 and
            abs(height - self.max_window_height) < 10
        )
        return is_fs
    
    def get_window_size(self) -> Tuple[int, int]:
        """
        Pencere boyutunu al.
        
        Returns:
            Tuple: (genişlik, yükseklik)
        """
        geometry = self.window.geometry()
        width_height = geometry.split("+")[0]
        width, height = map(int, width_height.split("x"))
        return width, height
    
    def get_window_position(self) -> Tuple[int, int]:
        """
        Pencere konumunu al.
        
        Returns:
            Tuple: (x, y)
        """
        geometry = self.window.geometry()
        position = geometry.split("+")[1:]
        x, y = map(int, position)
        return x, y


class AdaptiveLayout:
    """
    Uyarlanabilir Layout Yöneticisi.
    
    Ekran boyutuna göre layout'unu otomatik olarak ayarlar.
    - Küçük ekranda: Vertical layout (widget'lar alt alta)
    - Geniş ekranda: Horizontal layout (widget'lar yanyana)
    """
    
    def __init__(
        self,
        parent: Any,
        breakpoint_width: int = 1024
    ) -> None:
        """
        Adaptive Layout'u başlat.
        
        Args:
            parent: Parent widget
            breakpoint_width: Layout değişme noktası (piksel)
        """
        self.parent = parent
        self.breakpoint_width = breakpoint_width
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_horizontal = False
        
        # Bind'i ayarlayarak resize'ı dinle
        self.parent.bind("<Configure>", self._on_resize)
    
    def _on_resize(self, event: Any) -> None:
        """
        Resize event'ini işle ve layout'u ayarla.
        
        Args:
            event: Configure event
        """
        try:
            # Pencere genişliğine göre layout kararı ver
            if event.width >= self.breakpoint_width:
                if not self.is_horizontal:
                    self._switch_to_horizontal()
                    self.is_horizontal = True
            else:
                if self.is_horizontal:
                    self._switch_to_vertical()
                    self.is_horizontal = False
            
            self.logger.debug(
                f"Layout {'horizontal' if self.is_horizontal else 'vertical'}: "
                f"{event.width}px"
            )
        except Exception as e:
            self.logger.error(f"Layout resize error: {str(e)}")
    
    def _switch_to_horizontal(self) -> None:
        """Yatay layout'a geç (yan yana)"""
        # Alt sınıflar tarafından override edilebilir
        pass
    
    def _switch_to_vertical(self) -> None:
        """Dikey layout'a geç (alt alta)"""
        # Alt sınıflar tarafından override edilebilir
        pass


class ResponsiveDialog:
    """
    Responsive Modal Dialog.
    
    Ekran boyutuna göre dinamik boyut ve konumlandırma.
    Pencere boyutu otomatik ayarlanır, içerik tutmayı sağlar.
    """
    
    def __init__(
        self,
        parent: ctk.CTk,
        title: str,
        width: int = 500,
        height: int = 400,
        min_width: int = 300,
        min_height: int = 250
    ) -> None:
        """
        Responsive Dialog'u başlat.
        
        Args:
            parent: Parent penceresi (main window)
            title: Dialog başlığı
            width: Hedef genişlik (piksel)
            height: Hedef yükseklik (piksel)
            min_width: Minimum genişlik (piksel)
            min_height: Minimum yükseklik (piksel)
        """
        self.parent = parent
        self.title = title
        self.width = width
        self.height = height
        self.min_width = min_width
        self.min_height = min_height
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Dialog penceresi oluştur
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Responsive pencere yöneticisi
        self.responsive = ResponsiveWindow(parent)
        
        # Pencere boyutunu ayarla
        self._adjust_size()
        
        # Pencereyi ortala
        self.responsive.center_relative_to_parent(
            self.dialog, self.width, self.height
        )
        
        # Bind'i ayarlayarak resize'ı dinle
        self.dialog.bind("<Configure>", self._on_dialog_resize)
        
        self.logger.debug(f"ResponsiveDialog created: {title} ({width}x{height})")
    
    def _adjust_size(self) -> None:
        """
        Ekran boyutuna göre dialog boyutunu ayarla.
        
        Dialog'un ekrana taşan bir boyuta sahip olmaması sağlanır.
        """
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        
        # Maksimum boyutlar (ekranın %80'i)
        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)
        
        # Boyutu ayarla
        final_width = min(self.width, max_width)
        final_height = min(self.height, max_height)
        
        # Minimum boyutu sağla
        final_width = max(final_width, self.min_width)
        final_height = max(final_height, self.min_height)
        
        self.width = final_width
        self.height = final_height
        
        self.logger.debug(f"Dialog size adjusted: {final_width}x{final_height}")
    
    def _on_dialog_resize(self, event: Any) -> None:
        """
        Dialog resize event'ini işle.
        
        Args:
            event: Configure event
        """
        try:
            width = max(self.min_width, event.width)
            height = max(self.min_height, event.height)
            
            if width != event.width or height != event.height:
                self.dialog.geometry(f"{width}x{height}")
            
            self.logger.debug(f"Dialog resized: {width}x{height}")
        except Exception as e:
            self.logger.warning(f"Dialog resize error: {str(e)}")
    
    def get_frame(self) -> ctk.CTkFrame:
        """
        Dialog'un içerik frame'ini al.
        
        Returns:
            Dialog'un içerik frame'i
        """
        frame = ctk.CTkFrame(self.dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        return frame
    
    def show(self) -> None:
        """Dialog'u göster"""
        self.dialog.focus_force()
        self.parent.wait_window(self.dialog)
    
    def close(self) -> None:
        """Dialog'u kapat"""
        self.dialog.destroy()


# Yardımcı fonksiyonlar
def calculate_responsive_padding(
    screen_width: int,
    base_padding: int = 10,
    scaling_factor: float = 0.001
) -> int:
    """
    Ekran genişliğine göre responsive padding hesapla.
    
    Args:
        screen_width: Ekran genişliği (piksel)
        base_padding: Taban padding (piksel)
        scaling_factor: Ölçekleme faktörü
    
    Returns:
        Hesaplanan padding (piksel)
    """
    return int(base_padding + (screen_width * scaling_factor))


def calculate_responsive_font_size(
    base_size: int = 12,
    screen_width: int = 1920,
    scaling: bool = True
) -> int:
    """
    Ekran genişliğine göre responsive font boyutu hesapla.
    
    Args:
        base_size: Taban font boyutu (piksel)
        screen_width: Ekran genişliği (piksel)
        scaling: Ölçekleme aktif mi
    
    Returns:
        Hesaplanan font boyutu (piksel)
    """
    if not scaling:
        return base_size
    
    # 1920px genişlik'te base_size olacak şekilde hesapla
    ratio = screen_width / 1920
    return max(8, int(base_size * ratio))  # Minimum 8px


def get_responsive_breakpoints() -> Dict[str, int]:
    """
    Responsive design breakpoint'lerini al.
    
    Returns:
        Breakpoint'ler dictionary'si
    """
    return {
        "mobile": 480,          # 480px altında
        "tablet": 768,          # 480-768px arası
        "small_desktop": 1024,  # 768-1024px arası
        "desktop": 1280,        # 1024-1280px arası
        "large_desktop": 1920   # 1280px üstü
    }
