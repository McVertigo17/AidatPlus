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
from database.config import get_db_session

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
        # Use provided session or create context-managed one
        if db is not None:
            session = db
            return self._execute_create(data, session)
        
        with get_db_session() as session:
            return self._execute_create(data, session)
    
    def _execute_create(self, data: dict, session: Session) -> Daire:
        """Helper method to execute create logic"""
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
        if "kiraya_esias_alan" in data and data["kiraya_esias_alan"]:
            Validator.validate_positive_number(data.get("kiraya_esias_alan"), "Kiraya Esas Alan")
        
        # Isıtılan alan validasyonu (opsiyonel)
        if "isitilan_alan" in data and data["isitilan_alan"]:
            Validator.validate_positive_number(data.get("isitilan_alan"), "Isıtılan Alan")
        
        # Base class'ın create metodunu çağır
        return super().create(data, session)
    
    def update(self, id: int, data: dict, db: Optional[Session] = None) -> Optional[Daire]:
        """
        Daire güncelle ve validasyon yap.
        
        Args:
            id (int): Daire ID'si
            data (dict): Güncellenecek alanlar
                - daire_no (str, optional): Daire numarası
                - blok_id (int, optional): Blok ID'si
                - kat (int, optional): Kat numarası
                - kiraya_esia_alan (float, optional): Kiraya esia alan m²
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
        # Use provided session or create context-managed one
        if db is not None:
            session = db
            return self._execute_update(id, data, session)
        
        with get_db_session() as session:
            return self._execute_update(id, data, session)
    
    def _execute_update(self, id: int, data: dict, session: Session) -> Optional[Daire]:
        """Helper method to execute update logic"""
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
        if "kat" in data:
            if data["kat"] is not None:
                Validator.validate_integer(data["kat"], "Kat")
                Validator.validate_positive_number(data["kat"], "Kat")
            else:
                # Allow setting to None
                pass
        
        # Kiraya esas alan validasyonu (güncelleniyorsa)
        if "kiraya_esas_alan" in data:
            if data["kiraya_esas_alan"] is not None:
                # Validate that it can be converted to float
                try:
                    float(data["kiraya_esas_alan"])
                except (ValueError, TypeError):
                    raise ValidationError(
                        "Kiraya Esas Alan sayı olmalıdır",
                        code="VAL_002",
                        details={"field": "kiraya_esas_alan"}
                    )
                Validator.validate_positive_number(data["kiraya_esas_alan"], "Kiraya Esas Alan")
            else:
                # Allow setting to None
                pass
        
        # Isıtılan alan validasyonu (güncelleniyorsa)
        if "isitilan_alan" in data:
            if data["isitilan_alan"] is not None:
                # Validate that it can be converted to float
                try:
                    float(data["isitilan_alan"])
                except (ValueError, TypeError):
                    raise ValidationError(
                        "Isıtılan Alan sayı olmalıdır",
                        code="VAL_002",
                        details={"field": "isitilan_alan"}
                    )
                Validator.validate_positive_number(data["isitilan_alan"], "Isıtılan Alan")
            else:
                # Allow setting to None
                pass
        
        # Base class'ın update metodunu çağır
        return super().update(id, data, session)

    def get_by_blok(self, blok_id: int, db: Optional[Session] = None) -> List[Daire]:
        """Blok ID'sine göre daireleri getir"""
        if db is not None:
            result = db.query(Daire).filter(
                Daire.blok_id == blok_id,
                Daire.aktif == True
            ).all()
            return cast(List[Daire], result)
        
        with get_db_session() as session:
            result = session.query(Daire).filter(
                Daire.blok_id == blok_id,
                Daire.aktif == True
            ).all()
            return cast(List[Daire], result)

    def get_by_no_and_blok(self, daire_no: str, blok_id: int, db: Optional[Session] = None) -> Optional[Daire]:
        """Daire numarasına ve blok ID'sine göre daire getir"""
        if db is not None:
            result = db.query(Daire).filter(
                Daire.daire_no == daire_no,
                Daire.blok_id == blok_id,
                Daire.aktif == True
            ).first()
            return cast(Optional[Daire], result)
        
        with get_db_session() as session:
            result = session.query(Daire).filter(
                Daire.daire_no == daire_no,
                Daire.blok_id == blok_id,
                Daire.aktif == True
            ).first()
            return cast(Optional[Daire], result)

    def get_bos_daireler(self, db: Optional[Session] = None) -> List[Daire]:
        """Boş daireleri getir (sakini olmayan)"""
        if db is not None:
            result = db.query(Daire).options(
                joinedload(Daire.blok).joinedload('lojman')
            ).filter(
                Daire.aktif == True,
                Daire.sakini == None
            ).all()
            return cast(List[Daire], result)
        
        with get_db_session() as session:
            result = session.query(Daire).options(
                joinedload(Daire.blok).joinedload('lojman')
            ).filter(
                Daire.aktif == True,
                Daire.sakini == None
            ).all()
            return cast(List[Daire], result)

    def get_dolu_daireler(self, db: Optional[Session] = None) -> List[Daire]:
        """Dolu daireleri getir (sakini olan)"""
        if db is not None:
            result = db.query(Daire).options(
                joinedload(Daire.blok).joinedload('lojman'),
                joinedload(Daire.sakini)
            ).filter(
                Daire.aktif == True,
                Daire.sakini != None
            ).all()
            return cast(List[Daire], result)
        
        with get_db_session() as session:
            result = session.query(Daire).options(
                joinedload(Daire.blok).joinedload('lojman'),
                joinedload(Daire.sakini)
            ).filter(
                Daire.aktif == True,
                Daire.sakini != None
            ).all()
            return cast(List[Daire], result)

    def get_all_with_details(self, db: Optional[Session] = None) -> List[Daire]:
        """Tüm daireleri detaylarıyla birlikte getir"""
        if db is not None:
            result = db.query(Daire).options(
                joinedload(Daire.blok).joinedload('lojman'),
                joinedload(Daire.sakini)
            ).filter(Daire.aktif == True).all()
            return cast(List[Daire], result)
        
        with get_db_session() as session:
            result = session.query(Daire).options(
                joinedload(Daire.blok).joinedload('lojman'),
                joinedload(Daire.sakini)
            ).filter(Daire.aktif == True).all()
            return cast(List[Daire], result)
