"""
Aidat controller - Aidat işlemleri, ödemeleri ve validasyonlar.

Bu modül, aidat oluşturma, ödeme takibi ve aidat-spesifik
işlemleri gerçekleştirir.
"""

from typing import List, Optional, cast
from sqlalchemy.orm import Session, joinedload
from controllers.base_controller import BaseController
from models.base import AidatIslem, AidatOdeme, FinansIslem, Daire
from models.validation import Validator
from models.exceptions import ValidationError, NotFoundError
from database.config import get_db, get_db_session
from datetime import datetime

# Logger import
from utils.logger import get_logger

class AidatIslemController(BaseController[AidatIslem]):
    """
    Aidat işlemleri için controller.
    
    Aidat oluşturma, sorgu ve yönetimi işlemleri.
    
    Example:
        >>> controller = AidatIslemController()
        >>> aidatlar = controller.get_by_daire(5)
    """

    def __init__(self) -> None:
        super().__init__(AidatIslem)
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    def create(self, data: dict, db: Optional[Session] = None) -> AidatIslem:
        """
        Yeni aidat işlemi oluştur ve validasyon yap.
        
        Args:
            data (dict): Aidat verileri
                - daire_id (int): Daire ID'si (zorunlu)
                - ay (int): Ay (1-12)
                - yil (int): Yıl (pozitif sayı)
                - toplam_tutar (float): Toplam tutar (pozitif)
        
        Returns:
            AidatIslem: Oluşturulan aidat işlemi
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Daire bulunamadı ise
            DatabaseError: Veritabanı hatası
        
        Example:
            >>> data = {
            ...     "daire_id": 5,
            ...     "ay": 11,
            ...     "yil": 2024,
            ...     "toplam_tutar": 500.00
            ... }
            >>> aidat = controller.create(data)
        """
        if db is None:
            with get_db_session() as session:
                try:
                    # Daire ID validasyonu (zorunlu)
                    Validator.validate_required(data.get("daire_id"), "Daire")
                    Validator.validate_integer(data.get("daire_id"), "Daire ID'si")
                    Validator.validate_positive_number(data.get("daire_id"), "Daire ID'si")

                    # Daire var mı kontrol et
                    daire = session.query(Daire).filter(
                        Daire.id == data.get("daire_id"),
                        Daire.aktif == True
                    ).first()

                    if not daire:
                        raise NotFoundError(
                            f"Daire ID {data.get('daire_id')} bulunamadı",
                            code="NOT_FOUND_004",
                            details={"daire_id": data.get("daire_id")}
                        )

                    # Ay validasyonu
                    Validator.validate_required(data.get("ay"), "Ay")
                    Validator.validate_integer(data.get("ay"), "Ay")
                    Validator.validate_choice(
                        data.get("ay"), "Ay", list(range(1, 13))
                    )

                    # Yıl validasyonu
                    Validator.validate_required(data.get("yil"), "Yıl")
                    Validator.validate_integer(data.get("yil"), "Yıl")
                    Validator.validate_positive_number(data.get("yil"), "Yıl")

                    # Toplam tutar validasyonu
                    Validator.validate_required(data.get("toplam_tutar"), "Toplam Tutar")
                    Validator.validate_positive_number(data.get("toplam_tutar"), "Toplam Tutar")

                    # Base class'ın create metodunu çağır
                    return super().create(data, session)
                except (ValidationError, NotFoundError):
                    raise
        else:
            session = db
        
        try:
            # Daire ID validasyonu (zorunlu)
            Validator.validate_required(data.get("daire_id"), "Daire")
            Validator.validate_integer(data.get("daire_id"), "Daire ID'si")
            Validator.validate_positive_number(data.get("daire_id"), "Daire ID'si")
            
            # Daire var mı kontrol et
            daire = session.query(Daire).filter(
                Daire.id == data.get("daire_id"),
                Daire.aktif == True
            ).first()
            
            if not daire:
                raise NotFoundError(
                    f"Daire ID {data.get('daire_id')} bulunamadı",
                    code="NOT_FOUND_004",
                    details={"daire_id": data.get("daire_id")}
                )
            
            # Ay validasyonu
            Validator.validate_required(data.get("ay"), "Ay")
            Validator.validate_integer(data.get("ay"), "Ay")
            Validator.validate_choice(
                data.get("ay"), "Ay", list(range(1, 13))
            )
            
            # Yıl validasyonu
            Validator.validate_required(data.get("yil"), "Yıl")
            Validator.validate_integer(data.get("yil"), "Yıl")
            Validator.validate_positive_number(data.get("yil"), "Yıl")
            
            # Toplam tutar validasyonu
            Validator.validate_required(data.get("toplam_tutar"), "Toplam Tutar")
            Validator.validate_positive_number(data.get("toplam_tutar"), "Toplam Tutar")
            
            # Base class'ın create metodunu çağır
            return super().create(data, session)
        
        except (ValidationError, NotFoundError):
            raise
    
    def update(self, id: int, data: dict, db: Optional[Session] = None) -> Optional[AidatIslem]:
        """
        Aidat işlemi güncelle ve validasyon yap.
        
        Args:
            id (int): Aidat işlem ID'si
            data (dict): Güncellenecek alanlar
                - daire_id (int, optional): Daire ID'si
                - ay (int, optional): Ay (1-12)
                - yil (int, optional): Yıl
                - toplam_tutar (float, optional): Toplam tutar
        
        Returns:
            AidatIslem | None: Güncellenen aidat veya None
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Daire bulunamadı ise
        
        Example:
            >>> data = {"toplam_tutar": 550.00}
            >>> aidat = controller.update(1, data)
        """
        if db is None:
            with get_db_session() as session:
                try:
                    # Daire ID validasyonu (eğer güncelleniyorsa)
                    if "daire_id" in data and data["daire_id"] is not None:
                        Validator.validate_integer(data["daire_id"], "Daire ID'si")
                        Validator.validate_positive_number(data["daire_id"], "Daire ID'si")

                        # Daire var mı kontrol et
                        daire = session.query(Daire).filter(
                            Daire.id == data["daire_id"],
                            Daire.aktif == True
                        ).first()

                        if not daire:
                            raise NotFoundError(
                                f"Daire ID {data['daire_id']} bulunamadı",
                                code="NOT_FOUND_004",
                                details={"daire_id": data['daire_id']}
                            )

                    # Ay validasyonu (eğer güncelleniyorsa)
                    if "ay" in data and data["ay"]:
                        Validator.validate_integer(data["ay"], "Ay")
                        Validator.validate_choice(
                            data["ay"], "Ay", list(range(1, 13))
                        )

                    # Yıl validasyonu (eğer güncelleniyorsa)
                    if "yil" in data and data["yil"]:
                        Validator.validate_integer(data["yil"], "Yıl")
                        Validator.validate_positive_number(data["yil"], "Yıl")

                    # Toplam tutar validasyonu (eğer güncelleniyorsa)
                    if "toplam_tutar" in data and data["toplam_tutar"]:
                        Validator.validate_positive_number(data["toplam_tutar"], "Toplam Tutar")

                    # Base class'ın update metodunu çağır
                    return super().update(id, data, session)
                except (ValidationError, NotFoundError):
                    raise
        else:
            session = db
        
        try:
            # Daire ID validasyonu (eğer güncelleniyorsa)
            if "daire_id" in data and data["daire_id"] is not None:
                Validator.validate_integer(data["daire_id"], "Daire ID'si")
                Validator.validate_positive_number(data["daire_id"], "Daire ID'si")
                
                # Daire var mı kontrol et
                daire = session.query(Daire).filter(
                    Daire.id == data["daire_id"],
                    Daire.aktif == True
                ).first()
                
                if not daire:
                    raise NotFoundError(
                        f"Daire ID {data['daire_id']} bulunamadı",
                        code="NOT_FOUND_004",
                        details={"daire_id": data["daire_id"]}
                    )
            
            # Ay validasyonu (eğer güncelleniyorsa)
            if "ay" in data and data["ay"]:
                Validator.validate_integer(data["ay"], "Ay")
                Validator.validate_choice(
                    data["ay"], "Ay", list(range(1, 13))
                )
            
            # Yıl validasyonu (eğer güncelleniyorsa)
            if "yil" in data and data["yil"]:
                Validator.validate_integer(data["yil"], "Yıl")
                Validator.validate_positive_number(data["yil"], "Yıl")
            
            # Toplam tutar validasyonu (eğer güncelleniyorsa)
            if "toplam_tutar" in data and data["toplam_tutar"]:
                Validator.validate_positive_number(data["toplam_tutar"], "Toplam Tutar")
            
            # Base class'ın update metodunu çağır
            return super().update(id, data, session)
        
        except (ValidationError, NotFoundError):
            raise
        

    def get_by_daire(self, daire_id: int, db: Session = None) -> List[AidatIslem]:
        """Daire ID'sine göre aidat işlemlerini getir"""
        if db is None:
            with get_db_session() as session:
                result = session.query(AidatIslem).options(
                    joinedload(AidatIslem.daire).joinedload('blok').joinedload('lojman'),
                    joinedload(AidatIslem.odemeler).joinedload('finans_islem').joinedload('hesap')
                ).filter(
                    AidatIslem.daire_id == daire_id,
                    AidatIslem.aktif == True
                ).order_by(AidatIslem.yil.desc(), AidatIslem.ay.desc()).all()
                return cast(List[AidatIslem], result)
        else:
            result = db.query(AidatIslem).options(
                joinedload(AidatIslem.daire).joinedload('blok').joinedload('lojman'),
                joinedload(AidatIslem.odemeler).joinedload('finans_islem').joinedload('hesap')
            ).filter(
                AidatIslem.daire_id == daire_id,
                AidatIslem.aktif == True
            ).order_by(AidatIslem.yil.desc(), AidatIslem.ay.desc()).all()
            return cast(List[AidatIslem], result)

    def get_by_yil_ay(self, yil: int, ay: int, db: Session = None) -> List[AidatIslem]:
        """Yıl ve aya göre aidat işlemlerini getir"""
        if db is None:
            with get_db_session() as session:
                result = session.query(AidatIslem).options(
                    joinedload(AidatIslem.daire).joinedload('blok').joinedload('lojman'),
                    joinedload(AidatIslem.odemeler).joinedload('finans_islem').joinedload('hesap')
                ).filter(
                    AidatIslem.yil == yil,
                    AidatIslem.ay == ay,
                    AidatIslem.aktif == True
                ).all()
                return cast(List[AidatIslem], result)
        else:
            result = db.query(AidatIslem).options(
                joinedload(AidatIslem.daire).joinedload('blok').joinedload('lojman'),
                joinedload(AidatIslem.odemeler).joinedload('finans_islem').joinedload('hesap')
            ).filter(
                AidatIslem.yil == yil,
                AidatIslem.ay == ay,
                AidatIslem.aktif == True
            ).all()
            return cast(List[AidatIslem], result)

    def get_all_with_details(self, db: Session = None) -> List[AidatIslem]:
        """Tüm aidat işlemlerini detaylarıyla getir"""
        if db is None:
            with get_db_session() as session:
                result = session.query(AidatIslem).options(
                    joinedload(AidatIslem.daire).joinedload('blok').joinedload('lojman'),
                    joinedload(AidatIslem.odemeler).joinedload('finans_islem').joinedload('hesap')
                ).filter(
                    AidatIslem.aktif == True
                ).order_by(AidatIslem.yil.desc(), AidatIslem.ay.desc()).all()
                return cast(List[AidatIslem], result)
        else:
            result = db.query(AidatIslem).options(
                joinedload(AidatIslem.daire).joinedload('blok').joinedload('lojman'),
                joinedload(AidatIslem.odemeler).joinedload('finans_islem').joinedload('hesap')
            ).filter(
                AidatIslem.aktif == True
            ).order_by(AidatIslem.yil.desc(), AidatIslem.ay.desc()).all()
            return cast(List[AidatIslem], result)


class AidatOdemeController(BaseController[AidatOdeme]):
    """
    Aidat ödemeleri için controller.
    
    Ödeme kaydı, takibi ve yönetimi.
    
    Example:
        >>> controller = AidatOdemeController()
        >>> odemeler = controller.get_odeme_bekleyenler()
    """

    def __init__(self) -> None:
        super().__init__(AidatOdeme)
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    def create(self, data: dict, db: Optional[Session] = None) -> AidatOdeme:
        """
        Yeni aidat ödeme kaydı oluştur ve validasyon yap.
        
        Args:
            data (dict): Ödeme verileri
                - aidat_islem_id (int): Aidat işlem ID'si
                - son_odeme_tarihi (datetime): Son ödeme tarihi
                - odendi (bool): Ödendi mi?
        
        Returns:
            AidatOdeme: Oluşturulan ödeme kaydı
        
        Raises:
            ValidationError: Veri geçersiz ise
            DatabaseError: Veritabanı hatası
        """
        if db is None:
            with get_db_session() as session:
                try:
                    # Aidat işlem ID'si kontrolü
                    Validator.validate_required(data.get("aidat_islem_id"), "Aidat İşlem ID")
                    Validator.validate_integer(data.get("aidat_islem_id"), "Aidat İşlem ID")
                    
                    # Base class'ın create metodunu çağır
                    return super().create(data, session)
                except ValidationError:
                    raise
        else:
            session = db

            try:
                # Aidat işlem ID'si kontrolü
                Validator.validate_required(data.get("aidat_islem_id"), "Aidat İşlem ID")
                Validator.validate_integer(data.get("aidat_islem_id"), "Aidat İşlem ID")

                # Base class'ın create metodunu çağır
                return super().create(data, session)
            except ValidationError:
                raise

    def get_by_aidat_islem(self, aidat_islem_id: int, db: Session = None) -> List[AidatOdeme]:
        """Aidat işlem ID'sine göre ödemeleri getir"""
        if db is None:
            with get_db_session() as db_session:
                result = db_session.query(AidatOdeme).filter(
                    AidatOdeme.aidat_islem_id == aidat_islem_id
                ).order_by(AidatOdeme.created_at.desc()).all()
                return cast(List[AidatOdeme], result)
        else:
            result = db.query(AidatOdeme).filter(
                AidatOdeme.aidat_islem_id == aidat_islem_id
            ).order_by(AidatOdeme.created_at.desc()).all()
            return cast(List[AidatOdeme], result)

    def get_odeme_bekleyenler(self, db: Session = None) -> List[AidatOdeme]:
        """Ödeme bekleyen aidatları getir"""
        if db is None:
            with get_db_session() as db_session:
                result = db_session.query(AidatOdeme).options(
                    joinedload(AidatOdeme.aidat_islem).joinedload('daire').joinedload('blok').joinedload('lojman'),
                    joinedload(AidatOdeme.finans_islem).joinedload('hesap')
                ).filter(
                    AidatOdeme.odendi == False
                ).order_by(AidatOdeme.son_odeme_tarihi.asc()).all()
                return cast(List[AidatOdeme], result)
        else:
            result = db.query(AidatOdeme).options(
                joinedload(AidatOdeme.aidat_islem).joinedload('daire').joinedload('blok').joinedload('lojman'),
                joinedload(AidatOdeme.finans_islem).joinedload('hesap')
            ).filter(
                AidatOdeme.odendi == False
            ).order_by(AidatOdeme.son_odeme_tarihi.asc()).all()
            return cast(List[AidatOdeme], result)

    def get_odeme_yapilanlar(self, db: Session = None) -> List[AidatOdeme]:
        """Ödeme yapılan aidatları getir"""
        if db is None:
            with get_db_session() as db_session:
                result = db_session.query(AidatOdeme).options(
                    joinedload(AidatOdeme.aidat_islem).joinedload('daire').joinedload('blok').joinedload('lojman'),
                    joinedload(AidatOdeme.finans_islem).joinedload('hesap')
                ).filter(
                    AidatOdeme.odendi == True
                ).order_by(AidatOdeme.odeme_tarihi.desc()).all()
                return cast(List[AidatOdeme], result)
        else:
            result = db.query(AidatOdeme).options(
                joinedload(AidatOdeme.aidat_islem).joinedload('daire').joinedload('blok').joinedload('lojman'),
                joinedload(AidatOdeme.finans_islem).joinedload('hesap')
            ).filter(
                AidatOdeme.odendi == True
            ).order_by(AidatOdeme.odeme_tarihi.desc()).all()
            return cast(List[AidatOdeme], result)

    def odeme_yap(self, odeme_id: int, odeme_tarihi: datetime, finans_islem_id: Optional[int] = None, db: Optional[Session] = None) -> bool:
        """Ödeme yap (ödendi olarak işaretle)"""
        result = self.update(odeme_id, {
            "odendi": True,
            "odeme_tarihi": odeme_tarihi,
            "finans_islem_id": finans_islem_id
        }, db)
        return result is not None

    def odeme_iptal(self, odeme_id: int, db: Optional[Session] = None) -> bool:
        """Ödeme iptal et (ödenmedi olarak işaretle) ve ilişkili finans kaydını sil"""
        if db is None:
            with get_db_session() as db_session:
                db = db_session
                try:
                    # Önce ödemeyi al
                    odeme = self.get_by_id(odeme_id, db)
                    if odeme and odeme.finans_islem_id:
                        # İlişkili finans kaydını sil
                        finans_islem = db.query(FinansIslem).filter(
                            FinansIslem.id == odeme.finans_islem_id
                        ).first()
                        
                        if finans_islem:
                            # Finans controller aracılığıyla sil (bakiyeleri da güncelle)
                            from controllers.finans_islem_controller import FinansIslemController
                            finans_controller = FinansIslemController()
                            finans_controller.delete(finans_islem.id, db)
                    
                    # Ödemeyi iptal et
                    result = self.update(odeme_id, {
                        "odendi": False,
                        "odeme_tarihi": None,
                        "finans_islem_id": None
                    }, db)
                    return result is not None
                except Exception:
                    raise
        else:
            try:
                # Önce ödemeyi al
                odeme = self.get_by_id(odeme_id, db)
                if odeme and odeme.finans_islem_id:
                    # İlişkili finans kaydını sil
                    finans_islem = db.query(FinansIslem).filter(
                        FinansIslem.id == odeme.finans_islem_id
                    ).first()
                    
                    if finans_islem:
                        # Finans controller aracılığıyla sil (bakiyeleri da güncelle)
                        from controllers.finans_islem_controller import FinansIslemController
                        finans_controller = FinansIslemController()
                        finans_controller.delete(finans_islem.id, db)
                
                # Ödemeyi iptal et
                result = self.update(odeme_id, {
                    "odendi": False,
                    "odeme_tarihi": None,
                    "finans_islem_id": None
                }, db)
                return result is not None
            except Exception:
                raise
