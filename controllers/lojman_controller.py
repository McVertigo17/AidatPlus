"""
Lojman controller - Lojman yönetimi ve validasyonlar.

Bu modül, lojman (kompleks) CRUD işlemlerini gerçekleştirir.
"""

from typing import List, Optional, cast
from sqlalchemy.orm import Session, joinedload
from controllers.base_controller import BaseController
from models.base import Lojman
from models.validation import Validator
from models.exceptions import ValidationError
from database.config import get_db

# Logger import
from utils.logger import get_logger

class LojmanController(BaseController[Lojman]):
    """
    Lojman yönetimi için controller.
    
    Lojman kompleksi CRUD işlemleri.
    
    Example:
        >>> controller = LojmanController()
        >>> lojmanlar = controller.get_aktif_lojmanlar()
    """

    def __init__(self) -> None:
        super().__init__(Lojman)
        self.logger = get_logger(f"{self.__class__.__name__}")

    def create(self, data: dict, db: Optional[Session] = None) -> Lojman:
        """
        Yeni lojman oluştur ve validasyon yap.
        
        Args:
            data (dict): Lojman verileri
                - ad (str): Lojman adı (2-100 karakter)
                - adres (str): Adres (opsiyonel)
        
        Returns:
            Lojman: Oluşturulan lojman
        
        Raises:
            ValidationError: Veri geçersiz ise
            DatabaseError: Veritabanı hatası
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # Lojman adı validasyonu
            Validator.validate_required(data.get("ad"), "Lojman Adı")
            Validator.validate_string_length(
                data.get("ad", ""), "Lojman Adı", 2, 100
            )
            
            # Benzersiz ad kontrolü
            existing_lojman = session.query(Lojman).filter(
                Lojman.ad == data.get("ad"),
                Lojman.aktif == True
            ).first()
            
            if existing_lojman:
                raise ValidationError(
                    f"'{data.get('ad')}' adlı lojman zaten mevcut",
                    code="VAL_001"
                )
            
            # Adres validasyonu
            Validator.validate_required(data.get("adres"), "Adres")
            
            # Base class'ın create metodunu çağır
            return super().create(data, session)
        
        except ValidationError:
            raise
        finally:
            if close_db:
                session.close()
    
    def update(self, id: int, data: dict, db: Optional[Session] = None) -> Optional[Lojman]:
        """
        Lojman güncelle ve validasyon yap.
        
        Args:
            id (int): Lojman ID'si
            data (dict): Güncellenecek alanlar
        
        Returns:
            Lojman | None: Güncellenen lojman veya None
        
        Raises:
            ValidationError: Veri geçersiz ise
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # Lojman adı validasyonu
            if "ad" in data and data["ad"]:
                Validator.validate_string_length(
                    data["ad"], "Lojman Adı", 2, 100
                )
                
                # Benzersiz ad kontrolü (kendi adı hariç)
                existing_lojman = session.query(Lojman).filter(
                    Lojman.ad == data["ad"],
                    Lojman.aktif == True,
                    Lojman.id != id
                ).first()
                
                if existing_lojman:
                    raise ValidationError(
                        f"'{data['ad']}' adlı lojman zaten mevcut",
                        code="VAL_001"
                    )
            
            # Adres validasyonu
            if "adres" in data and data["adres"]:
                Validator.validate_required(data["adres"], "Adres")
            
            # Base class'ın update metodunu çağır
            return super().update(id, data, session)
        
        except ValidationError:
            raise
        finally:
            if close_db:
                session.close()

    def get_all_with_details(self, db: Session = None) -> List[Lojman]:
        """Tüm lojmanları detaylarıyla birlikte getir"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Lojman).options(
                joinedload(Lojman.bloklar).joinedload('daireler')
            ).filter(Lojman.aktif == True).all()
            return cast(List[Lojman], result)
        finally:
            if close_db:
                db.close()

    def get_aktif_lojmanlar(self, db: Session = None) -> List[Lojman]:
        """Aktif lojmanları getir"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Lojman).filter(Lojman.aktif == True).all()
            return cast(List[Lojman], result)
        finally:
            if close_db:
                db.close()

    def get_by_ad(self, ad: str, db: Session = None) -> Optional[Lojman]:
        """Ada göre lojman getir"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Lojman).filter(
                Lojman.ad == ad,
                Lojman.aktif == True
            ).first()
            return cast(Optional[Lojman], result)
        finally:
            if close_db:
                db.close()
