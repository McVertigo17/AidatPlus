"""
Daire controller - Daire yönetimi ve validasyonlar.

Bu modül, daire (konut) CRUD işlemlerini gerçekleştirir.
"""

from typing import List, Optional, cast
from sqlalchemy.orm import Session, joinedload
from controllers.base_controller import BaseController
from models.base import Daire, Blok
from models.validation import Validator
from models.exceptions import ValidationError, NotFoundError
from database.config import get_db

# Logger import
from utils.logger import get_logger

class DaireController(BaseController[Daire]):
    """
    Daire yönetimi için controller.
    
    Daire (konut) CRUD işlemleri.
    
    Example:
        >>> controller = DaireController()
        >>> daireler = controller.get_by_blok(1)
    """

    def __init__(self) -> None:
        super().__init__(Daire)
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    def create(self, data: dict, db: Optional[Session] = None) -> Daire:
        """
        Yeni daire oluştur ve validasyon yap.
        
        Args:
             data (dict): Daire verileri
                  - daire_no (str): Daire numarası (1-20 karakter)
                  - blok_id (int): Blok ID'si (zorunlu)
                  - kat (int): Kat numarası (pozitif)
                  - kiraya_esas_alan (float): Kiraya esas alan m² (pozitif)
                  - isitilan_alan (float): Isıtılan alan m² (pozitif)
        
        Returns:
            Daire: Oluşturulan daire
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Blok bulunamadı ise
            DatabaseError: Veritabanı hatası
        
        Example:
            >>> data = {
            ...     "daire_no": "101",
            ...     "blok_id": 1,
            ...     "kat": 1,
            ...     "kiraya_esas_alan": 80.5
            ... }
            >>> daire = controller.create(data)
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # Daire numarası validasyonu
            Validator.validate_required(data.get("daire_no"), "Daire Numarası")
            Validator.validate_string_length(
                data.get("daire_no", ""), "Daire Numarası", 1, 20
            )
            
            # Blok ID validasyonu (zorunlu)
            Validator.validate_required(data.get("blok_id"), "Blok")
            Validator.validate_integer(data.get("blok_id"), "Blok ID'si")
            Validator.validate_positive_number(data.get("blok_id"), "Blok ID'si")
            
            # Blok var mı kontrol et
            blok = session.query(Blok).filter(
                Blok.id == data.get("blok_id"),
                Blok.aktif == True
            ).first()
            
            if not blok:
                raise NotFoundError(
                    f"Blok ID {data.get('blok_id')} bulunamadı",
                    code="NOT_FOUND_002",
                    details={"blok_id": data.get("blok_id")}
                )
            
            # Kat validasyonu (opsiyonel)
            if "kat" in data and data["kat"]:
                Validator.validate_integer(data.get("kat"), "Kat")
                Validator.validate_positive_number(data.get("kat"), "Kat")
            
            # Kiraya esas alan validasyonu (opsiyonel)
            if "kiraya_esas_alan" in data and data["kiraya_esas_alan"]:
                Validator.validate_positive_number(data.get("kiraya_esas_alan"), "Kiraya Esas Alan")
            
            # Isıtılan alan validasyonu (opsiyonel)
            if "isitilan_alan" in data and data["isitilan_alan"]:
                Validator.validate_positive_number(data.get("isitilan_alan"), "Isıtılan Alan")
            
            # Base class'ın create metodunu çağır
            return super().create(data, session)
        
        except (ValidationError, NotFoundError):
            raise
        finally:
            if close_db:
                session.close()
    
    def update(self, id: int, data: dict, db: Optional[Session] = None) -> Optional[Daire]:
        """
        Daire güncelle ve validasyon yap.
        
        Args:
            id (int): Daire ID'si
            data (dict): Güncellenecek alanlar
                - daire_no (str, optional): Daire numarası
                - blok_id (int, optional): Blok ID'si
                - kat (int, optional): Kat numarası
                - kiraya_esas_alan (float, optional): Kiraya esas alan m²
                - isitilan_alan (float, optional): Isıtılan alan m²
        
        Returns:
            Daire | None: Güncellenen daire veya None
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Blok bulunamadı ise
        
        Example:
            >>> data = {"kat": 2}
            >>> daire = controller.update(1, data)
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # Daire numarası validasyonu (güncelleniyorsa)
            if "daire_no" in data and data["daire_no"]:
                Validator.validate_string_length(
                    data["daire_no"], "Daire Numarası", 1, 20
                )
            
            # Blok ID validasyonu (güncelleniyorsa)
            if "blok_id" in data and data["blok_id"] is not None:
                Validator.validate_integer(data["blok_id"], "Blok ID'si")
                Validator.validate_positive_number(data["blok_id"], "Blok ID'si")
                
                # Blok var mı kontrol et
                blok = session.query(Blok).filter(
                    Blok.id == data["blok_id"],
                    Blok.aktif == True
                ).first()
                
                if not blok:
                    raise NotFoundError(
                        f"Blok ID {data['blok_id']} bulunamadı",
                        code="NOT_FOUND_002",
                        details={"blok_id": data["blok_id"]}
                    )
            
            # Kat validasyonu (güncelleniyorsa)
            if "kat" in data and data["kat"]:
                Validator.validate_integer(data["kat"], "Kat")
                Validator.validate_positive_number(data["kat"], "Kat")
            
            # Kiraya esas alan validasyonu (güncelleniyorsa)
            if "kiraya_esas_alan" in data and data["kiraya_esas_alan"]:
                Validator.validate_positive_number(data["kiraya_esas_alan"], "Kiraya Esas Alan")
            
            # Isıtılan alan validasyonu (güncelleniyorsa)
            if "isitilan_alan" in data and data["isitilan_alan"]:
                Validator.validate_positive_number(data["isitilan_alan"], "Isıtılan Alan")
            
            # Base class'ın update metodunu çağır
            return super().update(id, data, session)
        
        except (ValidationError, NotFoundError):
            raise
        finally:
            if close_db:
                session.close()

    def get_by_blok(self, blok_id: int, db: Session = None) -> List[Daire]:
        """Blok ID'sine göre daireleri getir"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Daire).filter(
                Daire.blok_id == blok_id,
                Daire.aktif == True
            ).all()
            return cast(List[Daire], result)
        finally:
            if close_db:
                db.close()

    def get_by_no_and_blok(self, daire_no: str, blok_id: int, db: Session = None) -> Optional[Daire]:
        """Daire numarasına ve blok ID'sine göre daire getir"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Daire).filter(
                Daire.daire_no == daire_no,
                Daire.blok_id == blok_id,
                Daire.aktif == True
            ).first()
            return cast(Optional[Daire], result)
        finally:
            if close_db:
                db.close()

    def get_bos_daireler(self, db: Session = None) -> List[Daire]:
        """Boş daireleri getir (sakini olmayan)"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Daire).options(
                joinedload(Daire.blok).joinedload('lojman')
            ).filter(
                Daire.aktif == True,
                Daire.sakini == None
            ).all()
            return cast(List[Daire], result)
        finally:
            if close_db:
                db.close()

    def get_dolu_daireler(self, db: Session = None) -> List[Daire]:
        """Dolu daireleri getir (sakini olan)"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Daire).options(
                joinedload(Daire.blok).joinedload('lojman'),
                joinedload(Daire.sakini)
            ).filter(
                Daire.aktif == True,
                Daire.sakini != None
            ).all()
            return cast(List[Daire], result)
        finally:
            if close_db:
                db.close()

    def get_all_with_details(self, db: Session = None) -> List[Daire]:
        """Tüm daireleri detaylarıyla birlikte getir"""
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            result = db.query(Daire).options(
                joinedload(Daire.blok).joinedload('lojman'),
                joinedload(Daire.sakini)
            ).filter(Daire.aktif == True).all()
            return cast(List[Daire], result)
        finally:
            if close_db:
                db.close()
