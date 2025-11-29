"""
Blok controller - Blok yönetimi ve validasyonlar.

Bu modül, blok (bina) CRUD işlemlerini gerçekleştirir.
"""

from typing import List, Optional, cast
from sqlalchemy.orm import Session, joinedload
from controllers.base_controller import BaseController
from models.base import Blok, Lojman
from models.validation import Validator
from models.exceptions import ValidationError, NotFoundError
from database.config import get_db

# Logger import
from utils.logger import get_logger

class BlokController(BaseController[Blok]):
    """
    Blok yönetimi için controller.
    
    Blok (bina) CRUD işlemleri.
    
    Example:
        >>> controller = BlokController()
        >>> bloklar = controller.get_by_lojman(1)
    """

    def __init__(self) -> None:
        super().__init__(Blok)
        self.logger = get_logger(f"{self.__class__.__name__}")

    def create(self, data: dict, db: Optional[Session] = None) -> Blok:
        """
        Yeni blok oluştur ve validasyon yap.
        
        Args:
            data (dict): Blok verileri
                - ad (str): Blok adı (2-50 karakter)
                - lojman_id (int): Lojman ID'si (zorunlu)
                - kat_sayisi (int): Kat sayısı (pozitif)
        
        Returns:
            Blok: Oluşturulan blok
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Lojman bulunamadı ise
            DatabaseError: Veritabanı hatası
        
        Example:
            >>> data = {
            ...     "ad": "A",
            ...     "lojman_id": 1,
            ...     "kat_sayisi": 5
            ... }
            >>> blok = controller.create(data)
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # Blok adı validasyonu
            Validator.validate_required(data.get("ad"), "Blok Adı")
            Validator.validate_string_length(
                data.get("ad", ""), "Blok Adı", 2, 50
            )
            
            # Lojman ID validasyonu (zorunlu)
            Validator.validate_required(data.get("lojman_id"), "Lojman")
            Validator.validate_integer(data.get("lojman_id"), "Lojman ID'si")
            Validator.validate_positive_number(data.get("lojman_id"), "Lojman ID'si")
            
            # Lojman var mı kontrol et
            lojman = session.query(Lojman).filter(
                Lojman.id == data.get("lojman_id"),
                Lojman.aktif == True
            ).first()
            
            if not lojman:
                raise NotFoundError(
                    f"Lojman ID {data.get('lojman_id')} bulunamadı",
                    code="NOT_FOUND_001",
                    details={"lojman_id": data.get("lojman_id")}
                )
            
            # Kat sayısı validasyonu (opsiyonel)
            if "kat_sayisi" in data and data["kat_sayisi"]:
                Validator.validate_integer(data.get("kat_sayisi"), "Kat Sayısı")
                Validator.validate_positive_number(data.get("kat_sayisi"), "Kat Sayısı")
            
            # Base class'ın create metodunu çağır
            return super().create(data, session)
        
        except (ValidationError, NotFoundError):
            raise
        finally:
            if close_db:
                session.close()
    
    def update(self, id: int, data: dict, db: Optional[Session] = None) -> Optional[Blok]:
        """
        Blok güncelle ve validasyon yap.
        
        Args:
            id (int): Blok ID'si
            data (dict): Güncellenecek alanlar
                - ad (str, optional): Blok adı
                - lojman_id (int, optional): Lojman ID'si
                - kat_sayisi (int, optional): Kat sayısı
        
        Returns:
            Blok | None: Güncellenen blok veya None
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Lojman bulunamadı ise
        
        Example:
            >>> data = {"kat_sayisi": 6}
            >>> blok = controller.update(1, data)
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # Blok adı validasyonu (güncelleniyorsa)
            if "ad" in data and data["ad"]:
                Validator.validate_string_length(
                    data["ad"], "Blok Adı", 2, 50
                )
            
            # Lojman ID validasyonu (güncelleniyorsa)
            if "lojman_id" in data and data["lojman_id"] is not None:
                Validator.validate_integer(data["lojman_id"], "Lojman ID'si")
                Validator.validate_positive_number(data["lojman_id"], "Lojman ID'si")
                
                # Lojman var mı kontrol et
                lojman = session.query(Lojman).filter(
                    Lojman.id == data["lojman_id"],
                    Lojman.aktif == True
                ).first()
                
                if not lojman:
                    raise NotFoundError(
                        f"Lojman ID {data['lojman_id']} bulunamadı",
                        code="NOT_FOUND_001",
                        details={"lojman_id": data["lojman_id"]}
                    )
            
            # Kat sayısı validasyonu (güncelleniyorsa)
            if "kat_sayisi" in data and data["kat_sayisi"]:
                Validator.validate_integer(data["kat_sayisi"], "Kat Sayısı")
                Validator.validate_positive_number(data["kat_sayisi"], "Kat Sayısı")
            
            # Base class'ın update metodunu çağır
            return super().update(id, data, session)
        
        except (ValidationError, NotFoundError):
            raise
        finally:
            if close_db:
                session.close()

    def get_by_lojman(self, lojman_id: int, db: Session = None) -> List[Blok]:
        """Lojman ID'sine göre blokları getir"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Blok).filter(
                Blok.lojman_id == lojman_id,
                Blok.aktif == True
            ).all()
            return cast(List[Blok], result)
        finally:
            if close_db:
                db.close()

    def get_by_ad_and_lojman(self, ad: str, lojman_id: int, db: Session = None) -> Optional[Blok]:
        """Blok adına ve lojman ID'sine göre blok getir"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Blok).filter(
                Blok.ad == ad,
                Blok.lojman_id == lojman_id,
                Blok.aktif == True
            ).first()
            return cast(Optional[Blok], result)
        finally:
            if close_db:
                db.close()

    def get_all_with_details(self, db: Session = None) -> List[Blok]:
        """Tüm blokları detaylarıyla birlikte getir"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Blok).options(
                joinedload(Blok.daireler),
                joinedload(Blok.lojman)
            ).filter(Blok.aktif == True).all()
            return cast(List[Blok], result)
        finally:
            if close_db:
                db.close()
