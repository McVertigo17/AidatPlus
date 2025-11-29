"""
Veri doğrulama (Validation) yardımcıları.

Bu modül, tüm veri doğrulama işlemleri için fonksiyonlar içerir.
Form inputlarını, veri tiplerini ve format doğrulamalarını yapıştırır.

Kategori:
    - Metin validasyonları (ad, soyad, vb.)
    - Sayı validasyonları (tutar, kat, vb.)
    - TC Kimlik doğrulaması
    - Email doğrulaması
    - Telefon doğrulaması
    - Tarih doğrulaması
"""

import re
from datetime import datetime
from typing import Any, Optional, List
from decimal import Decimal

from models.exceptions import ValidationError


class Validator:
    """Veri doğrulama sınıfı"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> None:
        """
        Alanın boş olmadığını kontrol et.
        
        Args:
            value (Any): Kontrol edilecek değer
            field_name (str): Alan adı (Türkçe)
        
        Raises:
            ValidationError: Alan boşsa
        
        Example:
            >>> Validator.validate_required("Ali", "Ad")
            >>> Validator.validate_required("", "Ad")  # ValidationError
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(
                f"{field_name} boş bırakılamaz",
                code="VAL_001",
                details={"field": field_name}
            )
    
    @staticmethod
    def validate_string_length(
        value: str, 
        field_name: str,
        min_length: int = 1,
        max_length: int = 255
    ) -> None:
        """
        Metin uzunluğunu kontrol et.
        
        Args:
            value (str): Kontrol edilecek metin
            field_name (str): Alan adı
            min_length (int): Minimum uzunluk (default: 1)
            max_length (int): Maksimum uzunluk (default: 255)
        
        Raises:
            ValidationError: Uzunluk dışında ise
        
        Example:
            >>> Validator.validate_string_length("Ali", "Ad", 2, 50)
            >>> Validator.validate_string_length("A", "Ad", 2, 50)  # Error
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"{field_name} metin olmalıdır",
                code="VAL_002",
                details={"field": field_name, "type": type(value).__name__}
            )
        
        length = len(value.strip())
        
        if length < min_length:
            raise ValidationError(
                f"{field_name} en az {min_length} karakter olmalıdır",
                code="VAL_003",
                details={"field": field_name, "min_length": min_length}
            )
        
        if length > max_length:
            raise ValidationError(
                f"{field_name} maksimum {max_length} karakter olmalıdır",
                code="VAL_003",
                details={"field": field_name, "max_length": max_length}
            )
    
    @staticmethod
    def validate_tc_id(tc_id: str) -> None:
        """
        TC Kimlik doğrulaması (11 haneli).
        
        Kurallar:
            - Tam 11 hane
            - Tümü sayı
            - İlk hane 0 olamaz
            - Check digit doğrulaması
        
        Args:
            tc_id (str): TC kimlik numarası
        
        Raises:
            ValidationError: Format geçersiz ise
        
        Example:
            >>> Validator.validate_tc_id("12345678901")
            >>> Validator.validate_tc_id("0234567890")  # Error
        """
        tc_id = str(tc_id).strip()
        
        # Format kontrolü
        if not tc_id.isdigit() or len(tc_id) != 11:
            raise ValidationError(
                "TC Kimlik 11 haneli sayı olmalıdır",
                code="VAL_004",
                details={"field": "tc_id"}
            )
        
        # İlk hane 0 olamaz
        if tc_id[0] == '0':
            raise ValidationError(
                "TC Kimlik 0 ile başlayamaz",
                code="VAL_004",
                details={"field": "tc_id"}
            )
        
        # Luhn algoritması ile check digit doğrulaması
        # Basit check: Son hanenin doğru olup olmadığını kontrol et
        total = 0
        for i in range(10):
            digit = int(tc_id[i])
            if i % 2 == 0:
                total += digit * 7
            total += digit
        
        check_digit = total % 10
        if check_digit != int(tc_id[10]):
            raise ValidationError(
                "TC Kimlik numarası geçersiz (kontrol hanesi hatalı)",
                code="VAL_004",
                details={"field": "tc_id"}
            )
    
    @staticmethod
    def validate_email(email: str) -> None:
        """
        Email doğrulaması.
        
        Args:
            email (str): Email adresi
        
        Raises:
            ValidationError: Format geçersiz ise
        
        Example:
            >>> Validator.validate_email("ali@example.com")
            >>> Validator.validate_email("invalid-email")  # Error
        """
        email = str(email).strip()
        
        # Basit regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            raise ValidationError(
                "Geçersiz email adresi",
                code="VAL_004",
                details={"field": "email"}
            )
    
    @staticmethod
    def validate_phone(phone: str) -> None:
        """
        Telefon doğrulaması (Türkiye formatı).
        
        Kabul edilen formatlar:
            - 05331234567
            - 0533 123 45 67
            - +90 533 123 45 67
        
        Args:
            phone (str): Telefon numarası
        
        Raises:
            ValidationError: Format geçersiz ise
        
        Example:
            >>> Validator.validate_phone("05331234567")
            >>> Validator.validate_phone("1234567")  # Error
        """
        phone = str(phone).strip().replace(" ", "")
        
        # +90 ile başlarsa 0 ile başlamayan format
        if phone.startswith("+90"):
            phone = "0" + phone[3:]
        
        # Format kontrolü (0 ile başlayan, 11 haneli)
        if not re.match(r'^0\d{10}$', phone):
            raise ValidationError(
                "Geçersiz telefon numarası (11 haneli olmalıdır)",
                code="VAL_004",
                details={"field": "telefon"}
            )
    
    @staticmethod
    def validate_positive_number(
        value: Any,
        field_name: str,
        allow_zero: bool = False
    ) -> None:
        """
        Pozitif sayı doğrulaması.
        
        Args:
            value (Any): Kontrol edilecek değer
            field_name (str): Alan adı
            allow_zero (bool): 0 izin verilsin mi? (default: False)
        
        Raises:
            ValidationError: Negatif veya geçersiz sayı ise
        
        Example:
            >>> Validator.validate_positive_number(100, "Tutar")
            >>> Validator.validate_positive_number(-50, "Tutar")  # Error
        """
        try:
            num = float(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"{field_name} sayı olmalıdır",
                code="VAL_002",
                details={"field": field_name}
            )
        
        if allow_zero:
            if num < 0:
                raise ValidationError(
                    f"{field_name} negatif olamaz",
                    code="VAL_005",
                    details={"field": field_name}
                )
        else:
            if num <= 0:
                raise ValidationError(
                    f"{field_name} pozitif sayı olmalıdır",
                    code="VAL_005",
                    details={"field": field_name}
                )
    
    @staticmethod
    def validate_integer(value: Any, field_name: str) -> None:
        """
        Tamsayı doğrulaması.
        
        Args:
            value (Any): Kontrol edilecek değer
            field_name (str): Alan adı
        
        Raises:
            ValidationError: Tamsayı değilse
        
        Example:
            >>> Validator.validate_integer(5, "Kat")
            >>> Validator.validate_integer(5.5, "Kat")  # Error
        """
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValidationError(
                f"{field_name} tamsayı olmalıdır",
                code="VAL_002",
                details={"field": field_name}
            )
    
    @staticmethod
    def validate_date(date_str: Any, format_str: str = "%d.%m.%Y") -> datetime:
        """
        Tarih doğrulaması.
        
        Args:
            date_str (str | datetime): Tarih stringi veya datetime nesnesi
            format_str (str): Beklenen format (default: "%d.%m.%Y")
        
        Returns:
            datetime: Doğrulanan tarih
        
        Raises:
            ValidationError: Format geçersiz ise
        
        Example:
            >>> date = Validator.validate_date("25.12.2024")
            >>> date = Validator.validate_date(datetime(2024, 12, 25))
            >>> Validator.validate_date("25/12/2024")  # Error
        """
        # Eğer zaten datetime nesnesi ise, doğrudan döndür
        if isinstance(date_str, datetime):
            return date_str
        
        try:
            return datetime.strptime(str(date_str).strip(), format_str)
        except ValueError:
            raise ValidationError(
                f"Geçersiz tarih formatı. Beklenen: {format_str}",
                code="VAL_006",
                details={"field": "tarih", "format": format_str}
            )
    
    @staticmethod
    def validate_choice(value: Any, field_name: str, choices: List[Any]) -> None:
        """
        Değerin belirlenen seçeneklerden biri olduğunu kontrol et.
        
        Args:
            value (Any): Kontrol edilecek değer
            field_name (str): Alan adı
            choices (List[Any]): Geçerli seçenekler
        
        Raises:
            ValidationError: Seçenek dışında ise
        
        Example:
            >>> Validator.validate_choice("aktif", "Durum", ["aktif", "pasif"])
            >>> Validator.validate_choice("hata", "Durum", ["aktif", "pasif"])  # Error
        """
        if value not in choices:
            raise ValidationError(
                f"{field_name} şu değerlerden biri olmalıdır: {', '.join(map(str, choices))}",
                code="VAL_004",
                details={"field": field_name, "valid_choices": choices}
            )
    
    @staticmethod
    def validate_unique_field(
        session: Any,
        model_class: Any,
        field_name: str,
        value: Any,
        exclude_id: Optional[int] = None
    ) -> None:
        """
        Veritabanında alan benzersizliğini kontrol et.
        
        Args:
            session: SQLAlchemy session
            model_class: Model sınıfı
            field_name (str): Alan adı
            value (Any): Kontrol edilecek değer
            exclude_id (int, optional): Göz ardı edilecek ID (güncelleme için)
        
        Raises:
            ValidationError: Aynı değer varsa
        
        Example:
            >>> from models.base import Sakin
            >>> from database.config import get_db
            >>> session = get_db()
            >>> Validator.validate_unique_field(
            ...     session, Sakin, "tc_id", "12345678901"
            ... )
        """
        from models.exceptions import DuplicateError
        
        query = session.query(model_class).filter(
            getattr(model_class, field_name) == value
        )
        
        if exclude_id:
            query = query.filter(model_class.id != exclude_id)
        
        if query.first():
            raise DuplicateError(
                f"Bu {field_name} zaten kullanılıyor",
                code="DUP_001",
                details={"field": field_name}
            )


# ============================================================================
# Batch Validation Helper
# ============================================================================

class BatchValidator:
    """Birden fazla alanı bir seferde doğrulayan yardımcı sınıf"""
    
    def __init__(self) -> None:
        """
        Batch doğrulayıcı'yı başlat.
        
        Birden fazla hata toplamak ve hepsini aynı anda göstermek için kullanılır.
        """
        self.errors: dict = {}
    
    def add_error(self, field: str, message: str) -> None:
        """
        Hata ekle.
        
        Args:
            field: Hatalı alan adı
            message: Hata mesajı
        """
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)
    
    def has_errors(self) -> bool:
        """
        Hata var mı kontrol et.
        
        Returns:
            bool: Hata varsa True, yoksa False
        """
        return bool(self.errors)
    
    def get_errors(self) -> dict:
        """
        Tüm hataları döndür.
        
        Returns:
            dict: Alan adı -> hata mesajleri listesi
        """
        return self.errors
    
    def raise_if_errors(self) -> None:
        """
        Hata varsa ValidationError exception'ı fırla.
        
        Raises:
            ValidationError: Eğer hata listesi boş değilse
        """
        if self.has_errors():
            error_message = "Doğrulama hataları:\n"
            for field, messages in self.errors.items():
                error_message += f"  • {field}: {', '.join(messages)}\n"
            
            raise ValidationError(
                error_message.strip(),
                code="VAL_007",
                details={"fields": list(self.errors.keys())}
            )
