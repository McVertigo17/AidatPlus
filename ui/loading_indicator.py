"""
Loading Spinner ve Progress Indicator Widgets

Uzun işlemlerde kullanıcıya görsel geri bildirim sağlar.
"""

import customtkinter as ctk
from typing import Optional, Callable
from threading import Thread
import time


class LoadingSpinner(ctk.CTkFrame):
    """
    Dönen loading spinner widget.
    
    Uzun işlemler sırasında gösterilen dönen animasyon.
    
    Attributes:
        is_running: Spinner çalışıyor mu
        
    Example:
        >>> spinner = LoadingSpinner(parent, radius=30)
        >>> spinner.pack()
        >>> spinner.start()
        >>> # İşlem tamamlandığında
        >>> spinner.stop()
    """
    
    def __init__(
        self,
        parent,
        radius: int = 30,
        fg_color: str = "transparent",
        spinner_color: str = "#0055A4",
        **kwargs
    ):
        """
        LoadingSpinner başlat.
        
        Args:
            parent: Parent widget
            radius: Spinner yarıçapı (piksel)
            fg_color: Arka plan rengi
            spinner_color: Spinner rengi
        """
        super().__init__(parent, fg_color=fg_color, **kwargs)
        
        self.radius = radius
        self.spinner_color = spinner_color
        self.is_running = False
        self.rotation = 0
        
        # Canvas spinner'ı
        self.canvas = ctk.CTkCanvas(
            self,
            width=radius * 2,
            height=radius * 2,
            bg="transparent",
            highlightthickness=0
        )
        self.canvas.pack()
    
    def start(self) -> None:
        """Spinner'ı başlat"""
        if not self.is_running:
            self.is_running = True
            self._animate()
    
    def stop(self) -> None:
        """Spinner'ı durdur"""
        self.is_running = False
        self.canvas.delete("all")
    
    def _animate(self) -> None:
        """Animasyon loop"""
        if not self.is_running:
            return
        
        self.rotation = (self.rotation + 12) % 360
        
        # Canvas temizle
        self.canvas.delete("all")
        
        # Dönen çizgi çiz
        angle = self.rotation * 3.14159 / 180
        x1 = self.radius + self.radius * 0.6 * __import__('math').cos(angle)
        y1 = self.radius + self.radius * 0.6 * __import__('math').sin(angle)
        
        self.canvas.create_arc(
            5, 5,
            self.radius * 2 - 5, self.radius * 2 - 5,
            start=0,
            extent=270,
            fill=self.spinner_color,
            outline=self.spinner_color,
            width=3
        )
        
        # Sonraki frame
        self.after(50, self._animate)


class LoadingDialog(ctk.CTkToplevel):
    """
    Loading dialog - işlem sırasında gösterilen modal.
    
    Kullanıcı işlem tamamlanana kadar etkileşim yapamaz.
    
    Example:
        >>> dialog = LoadingDialog(parent, "Yedekleme yapılıyor...")
        >>> dialog.pack()
        >>> 
        >>> # Arka plan işlem
        >>> def long_operation():
        ...     time.sleep(3)
        ...     dialog.close()
        >>> 
        >>> thread = Thread(target=long_operation)
        >>> thread.start()
    """
    
    def __init__(
        self,
        parent,
        title: str = "İşlem Devam Ediyor...",
        message: str = "",
        show_progress: bool = False
    ):
        """
        Loading dialog başlat.
        
        Args:
            parent: Parent window
            title: Dialog başlığı
            message: Gösterilecek mesaj
            show_progress: Progress bar gösterilsin mi
        """
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        
        # Modal olarak ayarla
        self.transient(parent)
        self.attributes('-topmost', True)
        
        # Ana frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20)
        
        # Spinner
        self.spinner = LoadingSpinner(main_frame, radius=30)
        self.spinner.pack(pady=10)
        self.spinner.start()
        
        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text=title,
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Mesaj
        if message:
            message_label = ctk.CTkLabel(
                main_frame,
                text=message,
                font=("Arial", 11),
                text_color="gray"
            )
            message_label.pack(pady=5)
        
        # Progress bar (opsiyonel)
        if show_progress:
            self.progress = ctk.CTkProgressBar(main_frame, width=300)
            self.progress.pack(pady=10)
            self.progress.set(0)
        else:
            self.progress = None
        
        # Pencereyi ortala
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def update_progress(self, value: float) -> None:
        """
        Progress bar'ı güncelle (0.0 - 1.0).
        
        Args:
            value: Progress değeri (0.0 - 1.0)
        """
        if self.progress:
            self.progress.set(value)
            self.update()
    
    def update_message(self, message: str) -> None:
        """
        Dialog mesajını güncelle.
        
        Args:
            message: Yeni mesaj
        """
        # İlk label'ı bul ve güncelle
        for widget in self.winfo_children()[0].winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text=message)
                break
    
    def close(self) -> None:
        """Dialog'u kapat"""
        self.spinner.stop()
        self.destroy()


class ProgressIndicator(ctk.CTkFrame):
    """
    Progress bar ile ilerleme göstergesi.
    
    Dosya yüklemesi, yedekleme vb. işlemlerde kullanılır.
    
    Example:
        >>> progress = ProgressIndicator(parent)
        >>> progress.pack()
        >>> progress.set_max(100)
        >>> 
        >>> for i in range(101):
        ...     progress.set_value(i)
        ...     time.sleep(0.1)
    """
    
    def __init__(
        self,
        parent,
        fg_color: str = "transparent",
        show_percentage: bool = True,
        **kwargs
    ):
        """
        ProgressIndicator başlat.
        
        Args:
            parent: Parent widget
            fg_color: Arka plan rengi
            show_percentage: Yüzde gösterilsin mi
        """
        super().__init__(parent, fg_color=fg_color, **kwargs)
        
        self.current_value = 0
        self.max_value = 100
        
        # Container
        container = ctk.CTkFrame(self, fg_color=fg_color)
        container.pack(fill="x", padx=0, pady=5)
        
        # Label
        label_frame = ctk.CTkFrame(container, fg_color=fg_color)
        label_frame.pack(fill="x")
        
        self.title_label = ctk.CTkLabel(
            label_frame,
            text="İşlem Devam Ediyor...",
            font=("Arial", 11)
        )
        self.title_label.pack(side="left")
        
        if show_percentage:
            self.percentage_label = ctk.CTkLabel(
                label_frame,
                text="0%",
                font=("Arial", 11)
            )
            self.percentage_label.pack(side="right")
        else:
            self.percentage_label = None
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(container, height=8)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)
    
    def set_max(self, max_value: int) -> None:
        """
        Maksimum değeri ayarla.
        
        Args:
            max_value: Maksimum değer
        """
        self.max_value = max_value
    
    def set_value(self, value: int) -> None:
        """
        Mevcut değeri ayarla.
        
        Args:
            value: Mevcut değer
        """
        self.current_value = value
        percentage = (value / self.max_value * 100) if self.max_value > 0 else 0
        
        self.progress_bar.set(percentage / 100)
        
        if self.percentage_label:
            self.percentage_label.configure(text=f"{percentage:.0f}%")
        
        self.update()
    
    def set_title(self, title: str) -> None:
        """
        Başlığı ayarla.
        
        Args:
            title: Yeni başlık
        """
        self.title_label.configure(text=title)
    
    def increment(self, amount: int = 1) -> None:
        """
        Değeri artır.
        
        Args:
            amount: Artış miktarı (default: 1)
        """
        self.set_value(self.current_value + amount)
    
    def reset(self) -> None:
        """Değerleri sıfırla"""
        self.set_value(0)


def run_with_spinner(
    parent,
    func: Callable,
    title: str = "İşlem Devam Ediyor...",
    message: str = ""
) -> None:
    """
    Spinner ile işlem çalıştır (blocking değil).
    
    Args:
        parent: Parent window
        func: Çalıştırılacak fonksiyon
        title: Dialog başlığı
        message: Dialog mesajı
    
    Example:
        >>> def backup():
        ...     time.sleep(3)
        >>> 
        >>> run_with_spinner(root, backup, "Yedekleme", "Lütfen bekleyin...")
    """
    dialog = LoadingDialog(parent, title, message)
    
    def worker():
        try:
            func()
        finally:
            dialog.after(0, dialog.close)
    
    thread = Thread(target=worker, daemon=True)
    thread.start()


def run_with_progress(
    parent,
    func: Callable[[Callable[[int], None]], None],
    title: str = "İşlem Devam Ediyor...",
    max_value: int = 100
) -> None:
    """
    Progress bar ile işlem çalıştır.
    
    Args:
        parent: Parent window
        func: Fonksiyon (progress_callback parametresi alır)
        title: Dialog başlığı
        max_value: Maksimum ilerleme değeri
    
    Example:
        >>> def backup_with_progress(progress_fn):
        ...     for i in range(101):
        ...         progress_fn(i)
        ...         time.sleep(0.1)
        >>> 
        >>> run_with_progress(root, backup_with_progress, "Yedekleme", 100)
    """
    dialog = LoadingDialog(parent, title, show_progress=True)
    dialog.progress.configure(maximum=max_value)
    
    def worker():
        try:
            func(dialog.update_progress)
        finally:
            dialog.after(0, dialog.close)
    
    thread = Thread(target=worker, daemon=True)
    thread.start()
