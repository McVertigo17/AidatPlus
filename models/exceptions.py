"""
Custom exception sınıfları - Error handling sistemi

Bu modül, uygulamada kullanılan tüm custom exception'ları içerir.
Her exception türü spesifik bir hata durumunu temsil eder.

Kategoriler:
    - ValidationError: Veri doğrulama hataları
    - DatabaseError: Veritabanı işlem hataları
    - FileError: Dosya işleme hataları
    - ConfigError: Konfigürasyon hataları
    - BusinessLogicError: İş mantığı hataları
"""

from typing import Optional, Any


class AidatPlusException(Exception):
    """
    Aidat Plus uygulamasının temel exception sınıfı.
    
    Tüm custom exception'lar bu sınıftan türetilir.
    
    Attributes:
        message (str): Hata mesajı
        code (str): Hata kodu (opsiyonel)
        details (dict): Ek hata detayları (opsiyonel)
    """
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        details: Optional[dict] = None
    ):
        """
        Exception'ı başlat.
        
        Args:
            message (str): Hata mesajı (Türkçe)
            code (str, optional): Hata kodu (örn. "VAL_001")
            details (dict, optional): Ek detaylar
        """
        self.message = message
        self.code = code or "UNKNOWN"
        self.details = details or {}
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        """Formatlanmış hata mesajını döndür"""
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class ValidationError(AidatPlusException):
    """
    Veri doğrulama hatası.
    
    Kullanım alanları:
        - Boş alan kontrolü
        - Veri tipi uyumsuzluğu
        - Uzunluk limitesi aşılması
        - Format doğrulama (TC, email, vb.)
        - Benzersizlik kontrolü
    
    Example:
        >>> if not ad_soyad or len(ad_soyad) < 2:
        ...     raise ValidationError(
        ...         "Ad soyad en az 2 karakter olmalıdır",
        ...         code="VAL_001",
        ...         details={"field": "ad_soyad"}
        ...     )
    """
    pass


class DatabaseError(AidatPlusException):
    """
    Veritabanı işlem hatası.
    
    Kullanım alanları:
        - SQL sorgusunda hata
        - İşlem commit hatası
        - Referans bütünlüğü ihlali
        - Deadlock durumu
        - Veri tipinde uyumsuzluk
    
    Example:
        >>> try:
        ...     session.commit()
        ... except IntegrityError as e:
        ...     raise DatabaseError(
        ...         "Benzersiz kayıt oluşturulamadı",
        ...         code="DB_001",
        ...         details={"table": "sakinler"}
        ...     )
    """
    pass


class FileError(AidatPlusException):
    """
    Dosya işleme hatası.
    
    Kullanım alanları:
        - Dosya bulunamadı
        - İzin yok / read-only
        - Format hatası
        - Boyut limiti aşılması
        - Backup/Restore işlemleri
    
    Example:
        >>> try:
        ...     with open(filepath, 'r') as f:
        ...         data = json.load(f)
        ... except FileNotFoundError:
        ...     raise FileError(
        ...         "Kategori dosyası bulunamadı",
        ...         code="FILE_001",
        ...         details={"filepath": filepath}
        ...     )
    """
    pass


class ConfigError(AidatPlusException):
    """
    Konfigürasyon hatası.
    
    Kullanım alanları:
        - Ayar dosyası eksik
        - Konfigürasyon parametresi geçersiz
        - Environment variable eksik
        - Veritabanı bağlantı hatası
    
    Example:
        >>> if not database_path:
        ...     raise ConfigError(
        ...         "Veritabanı yolu tanımlanmamış",
        ...         code="CFG_001"
        ...     )
    """
    pass


class BusinessLogicError(AidatPlusException):
    """
    İş mantığı hatası.
    
    Kullanım alanları:
        - İş kuralı ihlali
        - Durum geçişi hatası
        - Gerekli ön koşullar karşılanmadığında
        - Hesaplama hataları
    
    Example:
        >>> if not sakin.daire_id:
        ...     raise BusinessLogicError(
        ...         "Sakin bir daireye atanmış olmalıdır",
        ...         code="BIZ_001",
        ...         details={"sakin_id": sakin.id}
        ...     )
    """
    pass


class DuplicateError(ValidationError):
    """
    Benzersizlik ihlali hatası.
    
    Kullanım alanları:
        - Aynı TC kimliği ile iki sakin
        - Aynı hesap numarası
        - Aynı lojman adı
    
    Example:
        >>> if sakin_var:
        ...     raise DuplicateError(
        ...         "Bu TC kimliğine sahip sakin zaten var",
        ...         code="DUP_001",
        ...         details={"tc_id": "12345678901"}
        ...     )
    """
    pass


class NotFoundError(BusinessLogicError):
    """
    Kayıt bulunamadı hatası.
    
    Kullanım alanları:
        - ID'ye göre kayıt yok
        - Foreign key referansı yok
        - Silinmiş veri erişimi
    
    Example:
        >>> sakin = get_sakin_by_id(123)
        >>> if not sakin:
        ...     raise NotFoundError(
        ...         "Sakin bulunamadı",
        ...         code="NOT_FOUND_001",
        ...         details={"sakin_id": 123}
        ...     )
    """
    pass


class InsufficientDataError(BusinessLogicError):
    """
    Yeterli veri hatası.
    
    Kullanım alanları:
        - Raporlamak için yeterli veri yok
        - Hesaplama için ön koşul verileri eksik
    
    Example:
        >>> if len(transactions) < 2:
        ...     raise InsufficientDataError(
        ...         "Trend analizi için en az 2 veri gereklidir",
        ...         code="INSUFF_001"
        ...     )
    """
    pass


# ============================================================================
# Hata Kodu Referansı
# ============================================================================
"""
ValidationError Kodları:
    VAL_001: Boş alan hatası
    VAL_002: Veri tipi uyumsuzluğu
    VAL_003: Uzunluk limitesi aşılması
    VAL_004: Format hatası (TC, email, vb.)
    VAL_005: Negatif değer hatası
    VAL_006: Tarih format hatası
    VAL_007: Alanlar eksik

DatabaseError Kodları:
    DB_001: SQL sorgusu hatası
    DB_002: Commit hatası
    DB_003: Referans bütünlüğü ihlali
    DB_004: Unique constraint ihlali
    DB_005: Veri tipi hatası
    DB_006: Bağlantı hatası
    DB_007: Transaction hatası

FileError Kodları:
    FILE_001: Dosya bulunamadı
    FILE_002: İzin yok
    FILE_003: Format hatası
    FILE_004: Boyut limitesi aşılması
    FILE_005: Yazma hatası
    FILE_006: Okuma hatası

ConfigError Kodları:
    CFG_001: Ayar dosyası eksik
    CFG_002: Parametre geçersiz
    CFG_003: Environment variable eksik
    CFG_004: Veritabanı bağlantı hatası

BusinessLogicError Kodları:
    BIZ_001: İş kuralı ihlali
    BIZ_002: Durum geçişi hatası
    BIZ_003: Ön koşul sağlanmadı
    BIZ_004: Hesaplama hatası

DuplicateError Kodları:
    DUP_001: Benzersiz kayıt ihlali
    DUP_002: Aynı ID zaten var

NotFoundError Kodları:
    NOT_FOUND_001: Kayıt bulunamadı
    NOT_FOUND_002: Referans bulunamadı
    NOT_FOUND_003: Silinmiş veri erişimi

InsufficientDataError Kodları:
    INSUFF_001: Yeterli veri yok
    INSUFF_002: Gerekli alan eksik
"""
