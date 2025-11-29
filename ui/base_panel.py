"""
Temel panel sınıfı
"""

import customtkinter as ctk
from typing import TYPE_CHECKING, Any, Optional

from utils.logger import get_logger

if TYPE_CHECKING:
    from main import COLORS

class BasePanel:
    """Temel panel sınıfı"""

    def __init__(self, parent: Any, title: str, colors: dict) -> None:
        """
        Temel panel'i başlat.
        
        Args:
            parent: Parent widget (genellikle main window)
            title: Panel başlığı (ör. "Sakin Yönetimi")
            colors: Renk dictionary'si (primary, secondary, background, vb.)
        """
        self.parent = parent
        self.title = title
        self.colors = colors
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug(f"Initializing panel: {title}")

        # Ana frame
        self.frame = ctk.CTkFrame(parent, fg_color=self.colors["background"])
        self.frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.setup_ui()
        self.logger.info(f"Panel setup completed: {title}")

    def setup_ui(self) -> None:
        """Alt sınıflar tarafından override edilecek"""
        pass

    def show_message(self, message: str, title: str = "Bilgi") -> None:
        """Bilgi mesajı göster"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)

    def show_error(self, message: str, title: str = "Hata") -> None:
        """Hata mesajı göster"""
        from tkinter import messagebox
        messagebox.showerror(title, message)

    def show_warning(self, message: str, title: str = "Uyarı") -> None:
        """Uyarı mesajı göster"""
        from tkinter import messagebox
        messagebox.showwarning(title, message)

    def ask_yes_no(self, message: str, title: str = "Onay") -> bool:
        """Evet/Hayır sorusu sor"""
        from tkinter import messagebox
        return messagebox.askyesno(title, message)
    
    def is_widget_valid(self, widget: Any) -> bool:
        """Widget'ın hala geçerli olup olmadığını kontrol et"""
        try:
            if widget:
                # Widget'ın winfo_exists() metodunu çağırarak geçerliliğini kontrol et
                return bool(widget.winfo_exists())
            return False
        except Exception:
            return False