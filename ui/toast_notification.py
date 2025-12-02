"""
Toast Notification Sistemi

İşlem tamamlandığında kısa süreli bildirim gösterir.
"""

import customtkinter as ctk
from typing import Literal, Callable, Optional
from threading import Thread
import time


class Toast(ctk.CTkFrame):
    """
    Toast notification widget.
    
    Ekranın köşesinde görünen kısa süreli bildirim.
    
    Attributes:
        notification_type: Bildirim türü (success, error, warning, info)
        
    Example:
        >>> toast = Toast(root, "Başarıyla kaydedildi!", "success")
        >>> toast.pack()
    """
    
    # Renkler
    COLORS = {
        "success": {"bg": "#28A745", "fg": "#FFFFFF"},
        "error": {"bg": "#DC3545", "fg": "#FFFFFF"},
        "warning": {"bg": "#FFC107", "fg": "#000000"},
        "info": {"bg": "#0055A4", "fg": "#FFFFFF"}
    }
    
    def __init__(
        self,
        parent,
        message: str,
        notification_type: Literal["success", "error", "warning", "info"] = "info",
        duration: int = 3000,
        **kwargs
    ):
        """
        Toast başlat.
        
        Args:
            parent: Parent widget
            message: Gösterilecek mesaj
            notification_type: Bildirim türü
            duration: Gösterilme süresi (ms)
        """
        super().__init__(
            parent,
            fg_color=self.COLORS[notification_type]["bg"],
            **kwargs
        )
        
        self.notification_type = notification_type
        self.duration = duration
        self.message = message
        
        # İçerik
        content = ctk.CTkLabel(
            self,
            text=message,
            font=("Arial", 11),
            text_color=self.COLORS[notification_type]["fg"],
            wraplength=250
        )
        content.pack(padx=15, pady=10)
        
        # Kendini kaldır timer
        self.after(duration, self._remove)
    
    def _remove(self) -> None:
        """Toast'u kaldır"""
        self.destroy()


class ToastManager:
    """
    Toast bildirimlerini yönet.
    
    Birden fazla toast'u kontrol eder, sırada beklet veya üst üste göster.
    
    Example:
        >>> manager = ToastManager(root)
        >>> manager.show_success("Başarıyla kaydedildi!")
        >>> manager.show_error("Hata oluştu!")
        >>> manager.show_warning("Uyarı mesajı")
        >>> manager.show_info("Bilgi mesajı")
    """
    
    def __init__(
        self,
        parent,
        position: Literal["top-right", "top-left", "bottom-right", "bottom-left"] = "top-right"
    ):
        """
        ToastManager başlat.
        
        Args:
            parent: Parent window
            position: Toast'ların görüneceği yer
        """
        self.parent = parent
        self.position = position
        self.toasts: list[ctk.CTkFrame] = []
        self.x_offset = 20
        self.y_offset = 20
        self.spacing = 10
    
    def _get_position(self, toast_height: int = 50) -> tuple[int, int]:
        """
        Toast'un gösterileceği pozisyonu hesapla.
        
        Args:
            toast_height: Toast yüksekliği
        
        Returns:
            (x, y) koordinatları
        """
        window_width = self.parent.winfo_width()
        window_height = self.parent.winfo_height()
        
        # Aktif toast'ların toplam yüksekliği
        total_height = sum(
            t.winfo_height() + self.spacing
            for t in self.toasts
            if t.winfo_exists()
        )
        
        if "top" in self.position:
            y = self.y_offset + total_height
        else:
            y = window_height - self.y_offset - toast_height - total_height
        
        if "right" in self.position:
            x = window_width - self.x_offset - 280  # Toast genişliği ~280
        else:
            x = self.x_offset
        
        return x, y
    
    def show(
        self,
        message: str,
        notification_type: Literal["success", "error", "warning", "info"] = "info",
        duration: int = 3000
    ) -> Toast:
        """
        Toast göster.
        
        Args:
            message: Mesaj
            notification_type: Bildirim türü
            duration: Gösterilme süresi (ms)
        
        Returns:
            Toast widget'ı
        """
        toast = Toast(
            self.parent,
            message,
            notification_type,
            duration,
            width=280,
            height=50
        )
        
        self.toasts.append(toast)
        toast.pack()
        
        # Pozisyon ayarla
        self.parent.update_idletasks()
        x, y = self._get_position(toast.winfo_height())
        
        # Place ile yerleştir
        toast.place(x=x, y=y, width=280)
        
        # Toast silindiğinde listeden çıkar
        def cleanup():
            if toast in self.toasts:
                self.toasts.remove(toast)
        
        toast.after(duration + 100, cleanup)
        
        return toast
    
    def show_success(
        self,
        message: str,
        duration: int = 3000
    ) -> Toast:
        """
        Başarı bildirimi göster.
        
        Args:
            message: Mesaj
            duration: Gösterilme süresi (ms)
        """
        return self.show(message, "success", duration)
    
    def show_error(
        self,
        message: str,
        duration: int = 4000
    ) -> Toast:
        """
        Hata bildirimi göster.
        
        Args:
            message: Mesaj
            duration: Gösterilme süresi (ms)
        """
        return self.show(message, "error", duration)
    
    def show_warning(
        self,
        message: str,
        duration: int = 3500
    ) -> Toast:
        """
        Uyarı bildirimi göster.
        
        Args:
            message: Mesaj
            duration: Gösterilme süresi (ms)
        """
        return self.show(message, "warning", duration)
    
    def show_info(
        self,
        message: str,
        duration: int = 3000
    ) -> Toast:
        """
        Bilgi bildirimi göster.
        
        Args:
            message: Mesaj
            duration: Gösterilme süresi (ms)
        """
        return self.show(message, "info", duration)
    
    def clear_all(self) -> None:
        """Tüm toast'ları kaldır"""
        for toast in list(self.toasts):
            if toast.winfo_exists():
                toast.destroy()
        self.toasts.clear()


class StatusBar(ctk.CTkFrame):
    """
    Durum çubuğu - pencere altında gösterilir.
    
    Uzun işlemlerin durumunu ve istatiğini gösterir.
    
    Example:
        >>> status_bar = StatusBar(root)
        >>> status_bar.pack(side="bottom", fill="x")
        >>> status_bar.set_status("Yedekleme yapılıyor...", "busy")
        >>> status_bar.set_status("Başarıyla tamamlandı!", "success")
    """
    
    def __init__(self, parent, **kwargs):
        """
        StatusBar başlat.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, fg_color="#F0F0F0", height=30, **kwargs)
        self.pack_propagate(False)
        
        # Container
        container = ctk.CTkFrame(self, fg_color="#F0F0F0")
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Status indicator (nokta)
        self.indicator = ctk.CTkLabel(
            container,
            text="●",
            font=("Arial", 12),
            text_color="#0055A4"
        )
        self.indicator.pack(side="left", padx=5)
        
        # Status text
        self.status_label = ctk.CTkLabel(
            container,
            text="Hazır",
            font=("Arial", 10),
            text_color="#212529"
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        
        # Saat
        self.time_label = ctk.CTkLabel(
            container,
            text="",
            font=("Arial", 9),
            text_color="#6C757D"
        )
        self.time_label.pack(side="right", padx=5)
        
        # Saat güncelle
        self._update_time()
    
    def _update_time(self) -> None:
        """Saati güncelle"""
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=now)
        self.after(1000, self._update_time)
    
    def set_status(
        self,
        message: str,
        status_type: Literal["idle", "busy", "success", "error", "warning"] = "idle"
    ) -> None:
        """
        Durum ayarla.
        
        Args:
            message: Durum mesajı
            status_type: Durum türü
        """
        colors = {
            "idle": "#0055A4",
            "busy": "#FFC107",
            "success": "#28A745",
            "error": "#DC3545",
            "warning": "#FFC107"
        }
        
        self.indicator.configure(text_color=colors.get(status_type, "#0055A4"))
        self.status_label.configure(text=message)
        self.update()
    
    def set_busy(self, message: str = "İşlem devam ediyor...") -> None:
        """
        Meşgul durum ayarla.
        
        Args:
            message: Durum mesajı
        """
        self.set_status(message, "busy")
    
    def set_success(self, message: str = "Başarıyla tamamlandı!") -> None:
        """
        Başarı durum ayarla.
        
        Args:
            message: Durum mesajı
        """
        self.set_status(message, "success")
    
    def set_error(self, message: str = "Hata oluştu!") -> None:
        """
        Hata durum ayarla.
        
        Args:
            message: Durum mesajı
        """
        self.set_status(message, "error")
    
    def set_idle(self, message: str = "Hazır") -> None:
        """
        Boş durum ayarla.
        
        Args:
            message: Durum mesajı
        """
        self.set_status(message, "idle")
