"""
Sakin controller - Sakin CRUD işlemleri ve validasyonlar.

Bu modül, sakinler için CRUD operasyonlarını ve sakin-spesifik
işlemleri gerçekleştirir (aktif/pasif yönetimi vb.).
"""

from typing import List, Optional, cast
from sqlalchemy.orm import Session, joinedload
from controllers.base_controller import BaseController
from models.base import Sakin
from models.validation import Validator
from models.exceptions import ValidationError
from database.config import get_db
from datetime import datetime
from utils.logger import get_logger

class SakinController(BaseController[Sakin]):
    """
    Sakin yönetimi için controller.
    
    CRUD operasyonları ve sakin-spesifik işlemleri gerçekleştirir.
    
    Example:
        >>> controller = SakinController()
        >>> sakinler = controller.get_aktif_sakinler()
    """

    def __init__(self) -> None:
        super().__init__(Sakin)
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    def create(self, data: dict, db: Session = None) -> Sakin:
        """
        Yeni sakin oluştur ve validasyon yap.
        
        Args:
            data (dict): Sakin verileri
                - ad_soyad (str): Ad-soyad (2-100 karakter)
                - daire_id (int): Daire ID'si (zorunlu)
                - telefon (str, optional): Telefon numarası
                - email (str, optional): Email adresi
                - tahsis_tarihi (str | datetime, optional): Tahsis tarihi (DD.MM.YYYY string veya datetime object)
                - giris_tarihi (str | datetime, optional): Giriş tarihi (DD.MM.YYYY string veya datetime object)
                - cikis_tarihi (str | datetime, optional): Çıkış tarihi (arşiv için)
        
        Returns:
            Sakin: Oluşturulan sakin nesnesi
        
        Raises:
            ValidationError: Veri geçersiz ise
            DatabaseError: Veritabanı hatası
        
        Example:
            >>> data = {
            ...     "ad_soyad": "Ali Yıldız",
            ...     "daire_id": 5,
            ...     "tahsis_tarihi": "01.01.2024"
            ... }
            >>> sakin = controller.create(data)
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # Ad-soyad validasyonu
            Validator.validate_required(data.get("ad_soyad"), "Ad-Soyad")
            Validator.validate_string_length(
                data.get("ad_soyad", ""), "Ad-Soyad", 2, 100
            )
            
            # Daire ID validasyonu (zorunlu)
            Validator.validate_required(data.get("daire_id"), "Daire")
            
            # Telefon validasyonu (opsiyonel)
            if data.get("telefon"):
                Validator.validate_phone(data.get("telefon", ""))
            
            # Email validasyonu (opsiyonel)
            if data.get("email"):
                Validator.validate_email(data.get("email", ""))
            
            # Tahsis tarihi validasyonu (opsiyonel)
            tahsis_tarihi = data.get("tahsis_tarihi")
            if tahsis_tarihi:
                # String veya datetime object olabilir
                if isinstance(tahsis_tarihi, str):
                    Validator.validate_date(tahsis_tarihi, "%d.%m.%Y")
            
            # Giriş tarihi validasyonu (opsiyonel)
            giris_tarihi = data.get("giris_tarihi")
            if giris_tarihi:
                # String veya datetime object olabilir
                if isinstance(giris_tarihi, str):
                    Validator.validate_date(giris_tarihi, "%d.%m.%Y")
            
            # Base class'ın create metodunu çağır
            return super().create(data, session)
        
        except ValidationError:
            raise
        finally:
            if close_db:
                session.close()
    
    def update(self, id: int, data: dict, db: Session = None) -> Optional[Sakin]:
        """
        Sakin güncelle ve validasyon yap.
        
        Args:
            id (int): Sakin ID'si
            data (dict): Güncellenecek alanlar
                - ad_soyad (str, optional): Ad-soyad (2-100 karakter)
                - daire_id (int, optional): Daire ID'si
                - telefon (str, optional): Telefon numarası
                - email (str, optional): Email adresi
                - tahsis_tarihi (str, optional): Tahsis tarihi (DD.MM.YYYY)
                - giris_tarihi (str, optional): Giriş tarihi (DD.MM.YYYY)
        
        Returns:
            Sakin | None: Güncellenen sakin veya None
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Sakin bulunamadı ise
        
        Example:
            >>> data = {"telefon": "+90 555 123 4567"}
            >>> sakin = controller.update(5, data)
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # Ad-soyad validasyonu (eğer güncelleniyorsa)
            if "ad_soyad" in data and data["ad_soyad"]:
                Validator.validate_string_length(
                    data["ad_soyad"], "Ad-Soyad", 2, 100
                )
            
            # Daire ID validasyonu (eğer güncelleniyorsa)
            if "daire_id" in data and data["daire_id"] is not None:
                Validator.validate_required(data["daire_id"], "Daire")
            
            # Telefon validasyonu
            if "telefon" in data and data["telefon"]:
                Validator.validate_phone(data["telefon"])
            
            # Email validasyonu
            if "email" in data and data["email"]:
                Validator.validate_email(data["email"])
            
            # Tahsis tarihi validasyonu (eğer güncelleniyorsa)
            if "tahsis_tarihi" in data and data["tahsis_tarihi"]:
                Validator.validate_date(data["tahsis_tarihi"], "%d.%m.%Y")
            
            # Giriş tarihi validasyonu (eğer güncelleniyorsa)
            if "giris_tarihi" in data and data["giris_tarihi"]:
                Validator.validate_date(data["giris_tarihi"], "%d.%m.%Y")
            
            # Base class'ın update metodunu çağır
            return super().update(id, data, session)
        
        except ValidationError:
            raise
        finally:
            if close_db:
                session.close()

    def get_aktif_sakinler(self, db: Session = None) -> List[Sakin]:
        """Aktif sakinleri getir"""
        self.logger.debug("Fetching active residents")
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            residents = db.query(Sakin).options(
                joinedload(Sakin.daire).joinedload('blok').joinedload('lojman')
            ).filter(
                Sakin.aktif == True,
                Sakin.cikis_tarihi == None  # Ayrılış tarihi olmayanlar aktif
            ).all()
            self.logger.info(f"Successfully fetched {len(residents)} active residents")
            return cast(List[Sakin], residents)
        except Exception as e:
            self.logger.error(f"Failed to fetch active residents: {str(e)}")
            raise
        finally:
            if close_db:
                db.close()

    def get_pasif_sakinler(self, db: Session = None) -> List[Sakin]:
        """Pasif sakinleri getir (arşiv)"""
        self.logger.debug("Fetching passive residents")
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            residents = db.query(Sakin).options(
                joinedload(Sakin.daire).joinedload('blok').joinedload('lojman'),
                joinedload(Sakin.eski_daire).joinedload('blok').joinedload('lojman')
            ).filter(
                Sakin.aktif == True,
                Sakin.cikis_tarihi != None  # Ayrılış tarihi olanlar pasif
            ).all()
            self.logger.info(f"Successfully fetched {len(residents)} passive residents")
            return cast(List[Sakin], residents)
        except Exception as e:
            self.logger.error(f"Failed to fetch passive residents: {str(e)}")
            raise
        finally:
            if close_db:
                db.close()

    def get_by_daire(self, daire_id: int, db: Session = None) -> List[Sakin]:
        """Daire ID'sine göre sakinleri getir"""
        self.logger.debug(f"Fetching residents for apartment id {daire_id}")
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            residents = db.query(Sakin).filter(
                Sakin.daire_id == daire_id,
                Sakin.aktif == True
            ).all()
            self.logger.info(f"Successfully fetched {len(residents)} residents for apartment id {daire_id}")
            return cast(List[Sakin], residents)
        except Exception as e:
            self.logger.error(f"Failed to fetch residents for apartment id {daire_id}: {str(e)}")
            raise
        finally:
            if close_db:
                db.close()

    def pasif_yap(self, sakin_id: int, cikis_tarihi: datetime, db: Session = None) -> bool:
        """Sakin'i pasif yap (arşive gönder) - daireden çıkar"""
        self.logger.debug(f"Setting resident id {sakin_id} as passive with exit date {cikis_tarihi}")
        if db is None:
            db = get_db()
            close_db = True
        else:
            close_db = False

        try:
            obj = db.query(Sakin).options(joinedload(Sakin.daire)).filter(Sakin.id == sakin_id).first()
            if obj:
                obj.cikis_tarihi = cikis_tarihi
                obj.eski_daire_id = obj.daire_id  # Geçmiş daireyi sakla
                obj.daire_id = None
                # Manuel daire güncelle
                if obj.daire:
                    obj.daire.sakini = None
                db.commit()
                db.refresh(obj)
                self.logger.info(f"Successfully set resident id {sakin_id} as passive")
                return True
            else:
                self.logger.warning(f"Resident with id {sakin_id} not found during passive operation")
                return False
        except Exception as e:
            self.logger.error(f"Failed to set resident id {sakin_id} as passive: {str(e)}")
            raise
        finally:
            if close_db:
                db.close()

    def aktif_yap(self, sakin_id: int, db: Session = None) -> bool:
        """Sakin'i aktif yap (arşivden çıkar)"""
        self.logger.debug(f"Setting resident id {sakin_id} as active")
        result = self.update(sakin_id, {
            "cikis_tarihi": None
        }, db)
        if result:
            self.logger.info(f"Successfully set resident id {sakin_id} as active")
            return True
        else:
            self.logger.warning(f"Failed to set resident id {sakin_id} as active - resident not found")
            return False

    def delete(self, id: int, db: Session = None) -> bool:
        """Sakini pasif sekmesinden kaldır (soft delete)
        
        Arayüzde gözükmez ama veritabanında veri kalır.
        Sadece aktif=False yapılır, hiçbir veri silinmez.
        Bu şekilde veri bütünlüğü ve denetim izi korunur.
        
        Args:
            id (int): Kaldırılacak sakin ID'si
            db (Session, optional): Veritabanı session'ı
        
        Returns:
            bool: İşlem başarılı ise True, başarısız ise False
        
        Raises:
            Exception: Veritabanı hatası
        """
        self.logger.debug(f"Removing resident with id {id} from view (soft delete)")
        session = db or get_db()
        close_db = db is None
        
        try:
            sakin = self.get_by_id(id, session)
            if not sakin:
                self.logger.warning(f"Resident with id {id} not found during delete")
                return False
            
            # Soft delete: sadece aktif=False yap
            sakin.aktif = False
            session.commit()
            self.logger.info(f"Successfully removed resident with id {id} from view (cikis_tarihi preserved: {sakin.cikis_tarihi})")
            return True
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to remove resident with id {id}: {str(e)}")
            raise
        finally:
            if close_db:
                session.close()

    def add_sakin(self, sakin_data: dict, db: Session = None) -> Sakin:
        """Yeni sakin ekle"""
        self.logger.debug(f"Adding new resident with data: {sakin_data}")
        result = self.create(sakin_data, db)
        self.logger.info(f"Successfully added new resident with id {result.id}")
        return result
