"""
Kategori yönetim controller - Kategori CRUD işlemleri ve validasyonlar.

Bu modül, ana ve alt kategorilerin yönetimi, oluşturma, güncelleme
ve silme işlemlerini gerçekleştirir.
"""

from typing import List, Optional, TypeVar, Generic, cast
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from controllers.base_controller import BaseController
from models.base import AnaKategori, AltKategori
from models.validation import Validator
from models.exceptions import ValidationError, NotFoundError, DuplicateError, BusinessLogicError
from database.config import get_db_session

# Logger import
from utils.logger import get_logger

T = TypeVar('T')

class KategoriYonetimController:
    """
    Kategori yönetimi için controller.
    
    Ana ve alt kategorilerin CRUD işlemleri.
    
    Example:
        >>> controller = KategoriYonetimController()
        >>> kategoriler = controller.get_ana_kategoriler()
    """

    def __init__(self) -> None:
        # Logger instance
        self.logger = get_logger(f"{self.__class__.__name__}")

    def get_ana_kategoriler(self, db: Optional[Session] = None) -> List[AnaKategori]:
        """
        Tüm ana kategorileri getir.
        
        Args:
            db (Session, optional): Veritabanı session'ı (context manager kullanırsa ignore edilir)
        
        Returns:
            List[AnaKategori]: Ana kategorilerin listesi
        """
        if db is not None:
            # Mevcut session ile çalış
            result = db.query(AnaKategori).options(joinedload(AnaKategori.alt_kategoriler)).all()
            return cast(List[AnaKategori], result)
        
        # Yeni session oluştur
        with get_db_session() as session:
            result = session.query(AnaKategori).options(joinedload(AnaKategori.alt_kategoriler)).all()
            return cast(List[AnaKategori], result)

    def get_ana_kategori_by_id(self, kategori_id: int, db: Optional[Session] = None) -> Optional[AnaKategori]:
        """
        ID ile ana kategori getir.
        
        Args:
            kategori_id (int): Ana kategori ID'si
            db (Session, optional): Veritabanı session'ı (context manager kullanırsa ignore edilir)
        
        Returns:
            AnaKategori | None: Bulunmuş kategori veya None
        
        Raises:
            ValidationError: kategori_id geçersiz ise
        """
        try:
            # Kategori ID validasyonu
            Validator.validate_required(kategori_id, "Kategori ID'si")
            Validator.validate_integer(kategori_id, "Kategori ID'si")
            Validator.validate_positive_number(kategori_id, "Kategori ID'si")
        except ValidationError:
            raise
        
        if db is not None:
            # Mevcut session ile çalış
            result = db.query(AnaKategori).filter(AnaKategori.id == kategori_id).first()
            return cast(Optional[AnaKategori], result)
        
        # Yeni session oluştur
        with get_db_session() as session:
            result = session.query(AnaKategori).filter(AnaKategori.id == kategori_id).first()
            return cast(Optional[AnaKategori], result)

    def create_ana_kategori(self, name: str, aciklama: Optional[str] = None, tip: str = "gelir", db: Optional[Session] = None) -> AnaKategori:
        """
        Yeni ana kategori oluştur ve validasyon yap.
        
        Args:
            name (str): Kategori adı (2-100 karakter)
            aciklama (str, optional): Kategori açıklaması
            tip (str): Kategori tipi ("gelir" veya "gider", default: "gelir")
            db (Session, optional): Veritabanı session'ı (context manager kullanırsa ignore edilir)
        
        Returns:
            AnaKategori: Oluşturulan ana kategori
        
        Raises:
            ValidationError: Veri geçersiz ise
            DuplicateError: Aynı adlı kategori varsa
        
        Example:
            >>> kategori = controller.create_ana_kategori("Gelirler", "Ana gelir kategorisi", "gelir")
        """
        # Kategori adı validasyonu
        Validator.validate_required(name, "Kategori Adı")
        Validator.validate_string_length(name, "Kategori Adı", 2, 100)
        
        # Tip validasyonu
        Validator.validate_required(tip, "Kategori Tipi")
        Validator.validate_choice(tip, "Kategori Tipi", ["gelir", "gider"])
        
        if db is not None:
            # Mevcut session ile çalış
            try:
                kategori = AnaKategori()
                kategori.name = name.strip()
                kategori.aciklama = aciklama
                kategori.tip = tip
                db.add(kategori)
                db.commit()
                db.refresh(kategori)
                return kategori
            except IntegrityError:
                db.rollback()
                raise DuplicateError(
                    f"'{name}' adlı ana kategori zaten var",
                    code="DUP_002",
                    details={"name": name}
                )
        
        # Yeni session oluştur
        with get_db_session() as session:
            try:
                kategori = AnaKategori()
                kategori.name = name.strip()
                kategori.aciklama = aciklama
                kategori.tip = tip
                session.add(kategori)
                session.commit()
                session.refresh(kategori)
                return kategori
            except IntegrityError:
                session.rollback()
                raise DuplicateError(
                    f"'{name}' adlı ana kategori zaten var",
                    code="DUP_002",
                    details={"name": name}
                )

    def update_ana_kategori(self, kategori_id: int, name: str, aciklama: Optional[str] = None, tip: str = "gelir", db: Optional[Session] = None) -> bool:
        """
        Ana kategoriyi güncelle ve validasyon yap.
        
        Args:
            kategori_id (int): Ana kategori ID'si
            name (str): Kategori adı (2-100 karakter)
            aciklama (str, optional): Kategori açıklaması
            tip (str): Kategori tipi ("gelir" veya "gider")
            db (Session, optional): Veritabanı session'ı (context manager kullanırsa ignore edilir)
        
        Returns:
            bool: Başarılı ise True, başarısız ise False
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Kategori bulunamadı ise
            DuplicateError: Aynı adlı kategori varsa
        
        Example:
            >>> success = controller.update_ana_kategori(1, "Gelirler Güncellenmiş")
        """
        try:
            # Kategori ID validasyonu
            Validator.validate_required(kategori_id, "Kategori ID'si")
            Validator.validate_integer(kategori_id, "Kategori ID'si")
            Validator.validate_positive_number(kategori_id, "Kategori ID'si")
            
            # Kategori adı validasyonu
            Validator.validate_required(name, "Kategori Adı")
            Validator.validate_string_length(name, "Kategori Adı", 2, 100)
            
            # Tip validasyonu
            Validator.validate_required(tip, "Kategori Tipi")
            Validator.validate_choice(tip, "Kategori Tipi", ["gelir", "gider"])
        except ValidationError:
            raise
        
        if db is not None:
            # Mevcut session ile çalış
            try:
                kategori = db.query(AnaKategori).filter(AnaKategori.id == kategori_id).first()
                if not kategori:
                    raise NotFoundError(
                        f"Ana kategori ID {kategori_id} bulunamadı",
                        code="NOT_FOUND_005",
                        details={"kategori_id": kategori_id}
                    )
                
                # Kategoriyi güncelle
                kategori.name = name.strip()
                kategori.aciklama = aciklama
                kategori.tip = tip
                db.commit()
                return True
            except IntegrityError:
                db.rollback()
                raise DuplicateError(
                    f"'{name}' adlı ana kategori zaten var",
                    code="DUP_002",
                    details={"name": name}
                )
        
        # Yeni session oluştur
        with get_db_session() as session:
            try:
                kategori = session.query(AnaKategori).filter(AnaKategori.id == kategori_id).first()
                if not kategori:
                    raise NotFoundError(
                        f"Ana kategori ID {kategori_id} bulunamadı",
                        code="NOT_FOUND_005",
                        details={"kategori_id": kategori_id}
                    )
                
                # Kategoriyi güncelle
                kategori.name = name.strip()
                kategori.aciklama = aciklama
                kategori.tip = tip
                session.commit()
                return True
            except IntegrityError:
                session.rollback()
                raise DuplicateError(
                    f"'{name}' adlı ana kategori zaten var",
                    code="DUP_002",
                    details={"name": name}
                )

    def delete_ana_kategori(self, kategori_id: int, db: Optional[Session] = None) -> bool:
        """
        Ana kategoriyi sil (alt kategorisi olmayanlar için).
        
        Args:
            kategori_id (int): Ana kategori ID'si
            db (Session, optional): Veritabanı session'ı (context manager kullanırsa ignore edilir)
        
        Returns:
            bool: Başarılı ise True, başarısız ise False
        
        Raises:
            ValidationError: kategori_id geçersiz ise
            NotFoundError: Kategori bulunamadı ise
            BusinessLogicError: Alt kategorisi varsa
        
        Example:
            >>> success = controller.delete_ana_kategori(1)
        """
        try:
            # Kategori ID validasyonu
            Validator.validate_required(kategori_id, "Kategori ID'si")
            Validator.validate_integer(kategori_id, "Kategori ID'si")
            Validator.validate_positive_number(kategori_id, "Kategori ID'si")
        except ValidationError:
            raise
        
        if db is not None:
            # Mevcut session ile çalış
            try:
                kategori = db.query(AnaKategori).filter(AnaKategori.id == kategori_id).first()
                if not kategori:
                    raise NotFoundError(
                        f"Ana kategori ID {kategori_id} bulunamadı",
                        code="NOT_FOUND_005",
                        details={"kategori_id": kategori_id}
                    )
                
                # Alt kategorisi varsa sil yapma
                if len(kategori.alt_kategoriler) > 0:
                    raise BusinessLogicError(
                        f"'{kategori.name}' kategorisinin alt kategorileri var. Önce alt kategorileri silin.",
                        code="BUS_LOGIC_001",
                        details={"kategori_id": kategori_id, "alt_kategori_sayisi": len(kategori.alt_kategoriler)}
                    )
                
                db.delete(kategori)
                db.commit()
                return True
            except (NotFoundError, BusinessLogicError):
                raise
            except Exception as e:
                db.rollback()
                raise ValidationError(
                    f"Ana kategori silinirken hata oluştu: {str(e)}",
                    code="VAL_008",
                    details={"kategori_id": kategori_id}
                )
        
        # Yeni session oluştur
        with get_db_session() as session:
            try:
                kategori = session.query(AnaKategori).filter(AnaKategori.id == kategori_id).first()
                if not kategori:
                    raise NotFoundError(
                        f"Ana kategori ID {kategori_id} bulunamadı",
                        code="NOT_FOUND_005",
                        details={"kategori_id": kategori_id}
                    )
                
                # Alt kategorisi varsa sil yapma
                if len(kategori.alt_kategoriler) > 0:
                    raise BusinessLogicError(
                        f"'{kategori.name}' kategorisinin alt kategorileri var. Önce alt kategorileri silin.",
                        code="BUS_LOGIC_001",
                        details={"kategori_id": kategori_id, "alt_kategori_sayisi": len(kategori.alt_kategoriler)}
                    )
                
                session.delete(kategori)
                session.commit()
                return True
            except (NotFoundError, BusinessLogicError):
                raise
            except Exception as e:
                session.rollback()
                raise ValidationError(
                    f"Ana kategori silinirken hata oluştu: {str(e)}",
                    code="VAL_008",
                    details={"kategori_id": kategori_id}
                )

    def get_alt_kategoriler(self, db: Optional[Session] = None) -> List[dict]:
        """
        Tüm alt kategorileri ve bağlı oldukları ana kategorileri getir.
        
        Args:
            db (Session, optional): Veritabanı session'ı (context manager kullanırsa ignore edilir)
        
        Returns:
            List[dict]: Alt kategorilerin listesi (id, name, parent_id, parent_name vb.)
        """
        if db is not None:
            # Mevcut session ile çalış
            alt_kategoriler = db.query(AltKategori).all()
            result = []
            for alt in alt_kategoriler:
                result.append({
                    "id": alt.id,
                    "name": alt.name,
                    "aciklama": alt.aciklama,
                    "parent_id": alt.parent_id,
                    "parent_name": alt.ana_kategori.name if alt.ana_kategori else None
                })
            return result
        
        # Yeni session oluştur
        with get_db_session() as session:
            alt_kategoriler = session.query(AltKategori).all()
            result = []
            for alt in alt_kategoriler:
                result.append({
                    "id": alt.id,
                    "name": alt.name,
                    "aciklama": alt.aciklama,
                    "parent_id": alt.parent_id,
                    "parent_name": alt.ana_kategori.name if alt.ana_kategori else None
                })
            return result

    def get_alt_kategoriler_by_parent(self, parent_id: int, db: Optional[Session] = None) -> List[AltKategori]:
        """
        Belirli bir ana kategoriye bağlı alt kategorileri getir.
        
        Args:
            parent_id (int): Ana kategori ID'si
            db (Session, optional): Veritabanı session'ı (context manager kullanırsa ignore edilir)
        
        Returns:
            List[AltKategori]: Alt kategorilerin listesi
        
        Raises:
            ValidationError: parent_id geçersiz ise
        """
        try:
            # Ana kategori ID validasyonu
            Validator.validate_required(parent_id, "Ana Kategori ID'si")
            Validator.validate_integer(parent_id, "Ana Kategori ID'si")
            Validator.validate_positive_number(parent_id, "Ana Kategori ID'si")
        except ValidationError:
            raise
        
        if db is not None:
            # Mevcut session ile çalış
            result = db.query(AltKategori).filter(AltKategori.parent_id == parent_id).all()
            return result or []
        
        # Yeni session oluştur
        with get_db_session() as session:
            result = session.query(AltKategori).filter(AltKategori.parent_id == parent_id).all()
            return result or []

    def create_alt_kategori(self, parent_id: int, name: str, aciklama: Optional[str] = None, db: Optional[Session] = None) -> AltKategori:
        """
        Yeni alt kategori oluştur ve validasyon yap.
        
        Args:
            parent_id (int): Ana kategori ID'si (zorunlu)
            name (str): Alt kategori adı (2-100 karakter)
            aciklama (str, optional): Alt kategori açıklaması
            db (Session, optional): Veritabanı session'ı (context manager kullanırsa ignore edilir)
        
        Returns:
            AltKategori: Oluşturulan alt kategori
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Ana kategori bulunamadı ise
            DuplicateError: Aynı adlı kategori varsa
        
        Example:
            >>> alt_kat = controller.create_alt_kategori(1, "Aidat Gelirleri")
        """
        try:
            # Ana kategori ID validasyonu
            Validator.validate_required(parent_id, "Ana Kategori ID'si")
            Validator.validate_integer(parent_id, "Ana Kategori ID'si")
            Validator.validate_positive_number(parent_id, "Ana Kategori ID'si")
            
            # Alt kategori adı validasyonu
            Validator.validate_required(name, "Alt Kategori Adı")
            Validator.validate_string_length(name, "Alt Kategori Adı", 2, 100)
        except ValidationError:
            raise
        
        if db is not None:
            # Mevcut session ile çalış
            try:
                # Ana kategorinin varlığını kontrol et
                parent = db.query(AnaKategori).filter(AnaKategori.id == parent_id).first()
                if not parent:
                    raise NotFoundError(
                        f"Ana kategori ID {parent_id} bulunamadı",
                        code="NOT_FOUND_006",
                        details={"parent_id": parent_id}
                    )

                alt_kategori = AltKategori()
                alt_kategori.parent_id = parent_id
                alt_kategori.name = name.strip()
                alt_kategori.aciklama = aciklama
                db.add(alt_kategori)
                db.commit()
                db.refresh(alt_kategori)
                return alt_kategori
            except IntegrityError:
                db.rollback()
                raise DuplicateError(
                    f"'{name}' adlı alt kategori zaten var",
                    code="DUP_003",
                    details={"name": name}
                )
        
        # Yeni session oluştur
        with get_db_session() as session:
            try:
                # Ana kategorinin varlığını kontrol et
                parent = session.query(AnaKategori).filter(AnaKategori.id == parent_id).first()
                if not parent:
                    raise NotFoundError(
                        f"Ana kategori ID {parent_id} bulunamadı",
                        code="NOT_FOUND_006",
                        details={"parent_id": parent_id}
                    )

                alt_kategori = AltKategori()
                alt_kategori.parent_id = parent_id
                alt_kategori.name = name.strip()
                alt_kategori.aciklama = aciklama
                session.add(alt_kategori)
                session.commit()
                session.refresh(alt_kategori)
                return alt_kategori
            except IntegrityError:
                session.rollback()
                raise DuplicateError(
                    f"'{name}' adlı alt kategori zaten var",
                    code="DUP_003",
                    details={"name": name}
                )

    def update_alt_kategori(self, kategori_id: int, name: str, aciklama: Optional[str] = None, parent_id: Optional[int] = None, db: Optional[Session] = None) -> bool:
        """
        Alt kategoriyi güncelle ve validasyon yap.
        
        Args:
            kategori_id (int): Alt kategori ID'si
            name (str): Alt kategori adı (2-100 karakter)
            aciklama (str, optional): Alt kategori açıklaması
            parent_id (int, optional): Ana kategori ID'si (ana kategoriyi değiştirmek için)
            db (Session, optional): Veritabanı session'ı (context manager kullanırsa ignore edilir)
        
        Returns:
            bool: Başarılı ise True, başarısız ise False
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Kategori veya ana kategori bulunamadı ise
            DuplicateError: Aynı adlı kategori varsa
        
        Example:
            >>> # Sadece adı güncelle
            >>> success = controller.update_alt_kategori(1, "Aidat Gelirleri Güncellenmiş")
            >>> # Adı ve ana kategoriyi güncelle
            >>> success = controller.update_alt_kategori(1, "Yeni Ad", parent_id=2)
        """
        try:
            # Kategori ID validasyonu
            Validator.validate_required(kategori_id, "Kategori ID'si")
            Validator.validate_integer(kategori_id, "Kategori ID'si")
            Validator.validate_positive_number(kategori_id, "Kategori ID'si")
            
            # Kategori adı validasyonu
            Validator.validate_required(name, "Alt Kategori Adı")
            Validator.validate_string_length(name, "Alt Kategori Adı", 2, 100)
            
            # Ana kategori ID validasyonu (eğer sağlanmışsa)
            if parent_id is not None:
                Validator.validate_integer(parent_id, "Ana Kategori ID'si")
                Validator.validate_positive_number(parent_id, "Ana Kategori ID'si")
        except ValidationError:
            raise
        
        if db is not None:
            # Mevcut session ile çalış
            try:
                kategori = db.query(AltKategori).filter(AltKategori.id == kategori_id).first()
                if not kategori:
                    raise NotFoundError(
                        f"Alt kategori ID {kategori_id} bulunamadı",
                        code="NOT_FOUND_007",
                        details={"kategori_id": kategori_id}
                    )
                
                # Ana kategoriyı değiştirmek istiyorsa yeni ana kategoriyi kontrol et ve güncelle
                if parent_id is not None:
                    yeni_parent = db.query(AnaKategori).filter(AnaKategori.id == parent_id).first()
                    if not yeni_parent:
                        raise NotFoundError(
                            f"Ana kategori ID {parent_id} bulunamadı",
                            code="NOT_FOUND_006",
                            details={"parent_id": parent_id}
                        )
                    # Ana kategorideği güncelle (farklı olsa da olmasa da)
                    kategori.parent_id = parent_id
                
                kategori.name = name.strip()
                kategori.aciklama = aciklama
                db.commit()
                return True
            except IntegrityError:
                db.rollback()
                raise DuplicateError(
                    f"'{name}' adlı alt kategori zaten var",
                    code="DUP_003",
                    details={"name": name}
                )
        
        # Yeni session oluştur
        with get_db_session() as session:
            try:
                kategori = session.query(AltKategori).filter(AltKategori.id == kategori_id).first()
                if not kategori:
                    raise NotFoundError(
                        f"Alt kategori ID {kategori_id} bulunamadı",
                        code="NOT_FOUND_007",
                        details={"kategori_id": kategori_id}
                    )
                
                # Ana kategoriyı değiştirmek istiyorsa yeni ana kategoriyi kontrol et ve güncelle
                if parent_id is not None:
                    yeni_parent = session.query(AnaKategori).filter(AnaKategori.id == parent_id).first()
                    if not yeni_parent:
                        raise NotFoundError(
                            f"Ana kategori ID {parent_id} bulunamadı",
                            code="NOT_FOUND_006",
                            details={"parent_id": parent_id}
                        )
                    # Ana kategorideği güncelle (farklı olsa da olmasa da)
                    kategori.parent_id = parent_id
                
                kategori.name = name.strip()
                kategori.aciklama = aciklama
                session.commit()
                return True
            except IntegrityError:
                session.rollback()
                raise DuplicateError(
                    f"'{name}' adlı alt kategori zaten var",
                    code="DUP_003",
                    details={"name": name}
                )

    def delete_alt_kategori(self, kategori_id: int, db: Optional[Session] = None) -> bool:
        """
        Alt kategoriyi sil.
        
        Args:
            kategori_id (int): Alt kategori ID'si
            db (Session, optional): Veritabanı session'ı (context manager kullanırsa ignore edilir)
        
        Returns:
            bool: Başarılı ise True, başarısız ise False
        
        Raises:
            ValidationError: kategori_id geçersiz ise
            NotFoundError: Kategori bulunamadı ise
            BusinessLogicError: Finans işleminde kullanılıyorsa
        
        Example:
            >>> success = controller.delete_alt_kategori(1)
        """
        try:
            # Kategori ID validasyonu
            Validator.validate_required(kategori_id, "Kategori ID'si")
            Validator.validate_integer(kategori_id, "Kategori ID'si")
            Validator.validate_positive_number(kategori_id, "Kategori ID'si")
        except ValidationError:
            raise
        
        if db is not None:
            # Mevcut session ile çalış
            try:
                kategori = db.query(AltKategori).filter(AltKategori.id == kategori_id).first()
                if not kategori:
                    raise NotFoundError(
                        f"Alt kategori ID {kategori_id} bulunamadı",
                        code="NOT_FOUND_007",
                        details={"kategori_id": kategori_id}
                    )
                
                # Finans işleminde kullanılıp kullanılmadığını kontrol et
                if len(kategori.finans_islemleri) > 0:
                    raise BusinessLogicError(
                        f"'{kategori.name}' kategorisi {len(kategori.finans_islemleri)} finans işleminde kullanılıyor. Silinemez.",
                        code="BUS_LOGIC_002",
                        details={"kategori_id": kategori_id, "islem_sayisi": len(kategori.finans_islemleri)}
                    )
                
                db.delete(kategori)
                db.commit()
                return True
            except (NotFoundError, BusinessLogicError):
                raise
            except Exception as e:
                db.rollback()
                raise ValidationError(
                    f"Alt kategori silinirken hata oluştu: {str(e)}",
                    code="VAL_008",
                    details={"kategori_id": kategori_id}
                )
        
        # Yeni session oluştur
        with get_db_session() as session:
            try:
                kategori = session.query(AltKategori).filter(AltKategori.id == kategori_id).first()
                if not kategori:
                    raise NotFoundError(
                        f"Alt kategori ID {kategori_id} bulunamadı",
                        code="NOT_FOUND_007",
                        details={"kategori_id": kategori_id}
                    )
                
                # Finans işleminde kullanılıp kullanılmadığını kontrol et
                if len(kategori.finans_islemleri) > 0:
                    raise BusinessLogicError(
                        f"'{kategori.name}' kategorisi {len(kategori.finans_islemleri)} finans işleminde kullanılıyor. Silinemez.",
                        code="BUS_LOGIC_002",
                        details={"kategori_id": kategori_id, "islem_sayisi": len(kategori.finans_islemleri)}
                    )
                
                session.delete(kategori)
                session.commit()
                return True
            except (NotFoundError, BusinessLogicError):
                raise
            except Exception as e:
                session.rollback()
                raise ValidationError(
                    f"Alt kategori silinirken hata oluştu: {str(e)}",
                    code="VAL_008",
                    details={"kategori_id": kategori_id}
                )
