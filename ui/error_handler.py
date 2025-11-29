"""
UI Error Handler - Arayüz hata yönetimi.

Bu modül, UI panellerinde oluşan hataları kullanıcı dostu mesajlarla
göstermek için yardımcı fonksiyonları içerir.

Functions:
    show_error: Hata dialog göster
    show_warning: Uyarı dialog göster
    show_success: Başarı mesajı göster
    handle_exception: Exception'ı işle ve göster
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Any, Union

from models.exceptions import (
    AidatPlusException,
    ValidationError,
    DatabaseError,
    FileError,
    ConfigError,
    BusinessLogicError,
    NotFoundError,
    DuplicateError,
    InsufficientDataError
)


def show_error(title: str, message: str, parent: Optional[tk.Misc] = None) -> None:
    """
    Hata dialog göster.
    
    Args:
        title (str): Dialog başlığı
        message (str): Hata mesajı (Türkçe)
        parent (tk.Misc, optional): Parent widget
    
    Example:
        >>> show_error("Hata", "Bu işlem başarısız oldu")
    """
    if parent is not None:
        messagebox.showerror(title, message, parent=parent)
    else:
        messagebox.showerror(title, message)


def show_warning(title: str, message: str, parent: Optional[tk.Misc] = None) -> None:
    """
    Uyarı dialog göster.
    
    Args:
        title (str): Dialog başlığı
        message (str): Uyarı mesajı (Türkçe)
        parent (tk.Misc, optional): Parent widget
    
    Example:
        >>> show_warning("Uyarı", "Bu işlemi onaylıyor musunuz?")
    """
    if parent is not None:
        messagebox.showwarning(title, message, parent=parent)
    else:
        messagebox.showwarning(title, message)


def show_success(title: str, message: str, parent: Optional[tk.Misc] = None) -> None:
    """
    Başarı mesajı göster.
    
    Args:
        title (str): Dialog başlığı
        message (str): Başarı mesajı (Türkçe)
        parent (tk.Misc, optional): Parent widget
    
    Example:
        >>> show_success("Başarılı", "Kayıt başarıyla oluşturuldu")
    """
    if parent is not None:
        messagebox.showinfo(title, message, parent=parent)
    else:
        messagebox.showinfo(title, message)


def handle_exception(
    exception: Exception,
    parent: Optional[Any] = None,
    fallback_callback: Optional[Callable] = None
) -> None:
    """
    Exception'ı işle ve kullanıcı dostu mesaj göster.
    
    Args:
        exception (Exception): Oluşan exception
        parent (tk.Widget, optional): Parent widget
        fallback_callback (Callable, optional): Exception işlenmediyse çağrılacak fonksiyon
    
    Example:
        >>> try:
        ...     sakin = controller.create(data)
        ... except Exception as e:
        ...     handle_exception(e, parent=self)
    """
    
    if isinstance(exception, ValidationError):
        show_error(
            "Doğrulama Hatası",
            f"Lütfen girdilerinizi kontrol edin:\n\n{exception.message}",
            parent=parent
        )
    
    elif isinstance(exception, DuplicateError):
        show_error(
            "Benzersizlik Hatası",
            f"{exception.message}",
            parent=parent
        )
    
    elif isinstance(exception, NotFoundError):
        show_error(
            "Bulunamadı",
            f"{exception.message}",
            parent=parent
        )
    
    elif isinstance(exception, DatabaseError):
        show_error(
            "Veritabanı Hatası",
            f"Veritabanı işlemi başarısız oldu:\n\n{exception.message}",
            parent=parent
        )
    
    elif isinstance(exception, FileError):
        show_error(
            "Dosya Hatası",
            f"Dosya işlemi başarısız oldu:\n\n{exception.message}",
            parent=parent
        )
    
    elif isinstance(exception, ConfigError):
        show_error(
            "Konfigürasyon Hatası",
            f"Uygulama konfigürasyonunda hata:\n\n{exception.message}",
            parent=parent
        )
    
    elif isinstance(exception, BusinessLogicError):
        show_warning(
            "İş Kuralı",
            f"{exception.message}",
            parent=parent
        )
    
    elif isinstance(exception, InsufficientDataError):
        show_warning(
            "Yetersiz Veri",
            f"{exception.message}",
            parent=parent
        )
    
    elif isinstance(exception, AidatPlusException):
        show_error(
            "Hata",
            f"{exception.message}",
            parent=parent
        )
    
    else:
        # Bilinmeyen exception
        error_message = f"Beklenmeyen hata oluştu:\n\n{str(exception)}"
        show_error("Sistem Hatası", error_message, parent=parent)
        
        # Fallback callback çalıştır
        if fallback_callback:
            try:
                fallback_callback()
            except Exception:
                pass


def validate_form_inputs(
    inputs: dict,
    required_fields: Optional[list] = None,
    parent: Optional[Any] = None
) -> bool:
    """
    Form inputlarını doğrula.
    
    Args:
        inputs (dict): Input field'ları (key -> value)
        required_fields (list, optional): Zorunlu alanlar
        parent (tk.Widget, optional): Parent widget
    
    Returns:
        bool: True (valid), False (invalid)
    
    Example:
        >>> inputs = {
        ...     "ad_soyad": entry_ad.get(),
        ...     "tc_id": entry_tc.get()
        ... }
        >>> if validate_form_inputs(inputs, ["ad_soyad", "tc_id"]):
        ...     # Form valid, işlem yap
        ...     pass
    """
    
    if required_fields is None:
        required_fields = list(inputs.keys())
    
    # Zorunlu alanları kontrol et
    empty_fields = []
    for field in required_fields:
        if field in inputs:
            value = inputs[field]
            if value is None or (isinstance(value, str) and not value.strip()):
                empty_fields.append(field)
    
    if empty_fields:
        message = "Lütfen şu alanları doldurun:\n"
        for field in empty_fields:
            message += f"  • {field}\n"
        
        show_error("Eksik Alan", message.strip(), parent=parent)
        return False
    
    return True


class ErrorHandler:
    """
    Error handling context manager.
    
    Kullanım:
        with ErrorHandler(parent=self):
            # Hatalı olabilecek kod
            sakin = controller.create(data)
    """
    
    def __init__(
        self,
        parent: Optional[Any] = None,
        show_success_msg: bool = False,
        success_message: str = "İşlem başarıyla tamamlandı"
    ):
        """
        ErrorHandler'ı başlat.
        
        Args:
            parent (tk.Widget, optional): Parent widget
            show_success_msg (bool): Başarı mesajı gösterilsin mi?
            success_message (str): Başarı mesajı
        """
        self.parent = parent
        self.show_success_msg = show_success_msg
        self.success_message = success_message
    
    def __enter__(self) -> 'ErrorHandler':
        """
        Context manager giriş.
        
        Returns:
            ErrorHandler: Kendi instance'ı
        """
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Optional[bool]:
        """
        Exception işle.
        
        Returns:
            bool: True (exception handled), False (re-raise)
        """
        if exc_type is None:
            # Exception yoksa, başarı mesajı göster
            if self.show_success_msg:
                show_success("Başarılı", self.success_message, parent=self.parent)
            return True
        
        if issubclass(exc_type, AidatPlusException):
            handle_exception(exc_val, parent=self.parent)
            return True  # Exception'ı handle et
        
        # Bilinmeyen exception'ı handle et
        handle_exception(exc_val, parent=self.parent)
        return True


# ============================================================================
# UI Input Validators
# ============================================================================

class UIValidator:
    """UI input'ları için doğrulama yardımcıları"""
    
    @staticmethod
    def validate_text_entry(
        entry_widget: Any,
        field_name: str,
        min_length: int = 1,
        max_length: int = 255,
        parent: Optional[Any] = None
    ) -> Optional[str]:
        """
        Text entry widget'ını doğrula.
        
        Args:
            entry_widget: Entry widget
            field_name (str): Alan adı
            min_length (int): Minimum uzunluk
            max_length (int): Maksimum uzunluk
            parent: Parent widget
        
        Returns:
            str | None: Doğrulanmış metin veya None
        """
        # CTkTextbox için özel işlem
        if hasattr(entry_widget, "get") and hasattr(entry_widget, "insert"):
            try:
                # Önce normal get() metodunu dene
                value = entry_widget.get().strip()
            except TypeError:
                # CTkTextbox ise indeks parametreleriyle get() çağrısı
                value = entry_widget.get("1.0", "end").strip()
                # CTkTextbox sonunda newline karakteri ekler, onu kaldır
                if value.endswith('\n'):
                    value = value[:-1]
        else:
            value = entry_widget.get().strip()
        
        if not value:
            show_error("Boş Alan", f"{field_name} boş bırakılamaz", parent=parent)
            entry_widget.focus()
            return None
        
        if len(value) < min_length:
            show_error(
                "Hata",
                f"{field_name} en az {min_length} karakter olmalıdır",
                parent=parent
            )
            entry_widget.focus()
            return None
        
        if len(value) > max_length:
            show_error(
                "Hata",
                f"{field_name} maksimum {max_length} karakter olmalıdır",
                parent=parent
            )
            entry_widget.focus()
            return None
        
        return value if value else None

    @staticmethod
    def validate_number_entry(
        entry_widget: Any,
        field_name: str,
        allow_negative: bool = False,
        allow_zero: bool = True,
        parent: Optional[Any] = None
    ) -> Optional[float]:
        """
        Sayı entry widget'ını doğrula.
        
        Args:
            entry_widget: Entry widget
            field_name (str): Alan adı
            allow_negative (bool): Negatif sayılar izin verilsin mi?
            allow_zero (bool): Sıfır izin verilsin mi?
            parent: Parent widget
        
        Returns:
            float | None: Doğrulanmış sayı veya None
        """
        value = entry_widget.get().strip()
        
        if not value:
            show_error("Boş Alan", f"{field_name} boş bırakılamaz", parent=parent)
            entry_widget.focus()
            return None
        
        try:
            num = float(value)
        except ValueError:
            show_error("Hata", f"{field_name} sayı olmalıdır", parent=parent)
            entry_widget.focus()
            return None
        
        if not allow_negative and num < 0:
            show_error("Hata", f"{field_name} negatif olamaz", parent=parent)
            entry_widget.focus()
            return None
        
        if not allow_zero and num == 0:
            show_error("Hata", f"{field_name} sıfır olamaz", parent=parent)
            entry_widget.focus()
            return None
        
        return num
    
    @staticmethod
    def validate_combobox(
        combobox_widget: Any,
        field_name: str,
        parent: Optional[Any] = None
    ) -> Optional[str]:
        """
        Combobox widget'ını doğrula.
        
        Args:
            combobox_widget: Combobox widget
            field_name (str): Alan adı
            parent: Parent widget
        
        Returns:
            str | None: Doğrulanmış seçim veya None
        """
        value = combobox_widget.get().strip()
        
        if not value:
            show_error("Boş Alan", f"Lütfen {field_name} seçin", parent=parent)
            combobox_widget.focus()
            return None
        
        return value if value else None
