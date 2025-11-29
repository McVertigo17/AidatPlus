"""
Sakin controller - Sakin CRUD işlemleri ve validasyonlar.

Bu modül, sakinler için CRUD operasyonlarını ve sakin-spesifik
işlemleri gerçekleştirir (aktif/pasif yönetimi vb.).
"""

from typing import List, Optional, cast, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from controllers.base_controller import BaseController
from models.base import Sakin
from models.validation import Validator
from models.exceptions import ValidationError
from database.config import get_db
from datetime import datetime, date
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
    
    def _parse_date(self, date_value: Union[str, datetime, date, None]) -> Optional[datetime]:
        """
        Tarih değerini parsing et (String/datetime/date → datetime).
        
        Args:
            date_value: Tarih değeri (str DD.MM.YYYY, datetime, date, None)
        
        Returns:
            datetime: Parsed datetime object veya None
        
        Raises:
            ValidationError: Geçersiz tarih formatı
        
        Example:
            >>> parsed = controller._parse_date("01.01.2024")
            >>> parsed = controller._parse_date(datetime.now())
        """
        if date_value is None:
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, date):
            return datetime.combine(date_value, datetime.min.time())
        
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, "%d.%m.%Y")
            except ValueError:
                raise ValidationError(
                    "Geçersiz tarih formatı. DD.MM.YYYY kullanınız.",
                    code="VAL_SAKN_004"
                )
        
        raise ValidationError(
            "Tarih String, datetime veya date türünde olmalıdır.",
            code="VAL_SAKN_004"
        )
    
    def _validate_daire_tarih_cakmasi(
        self, 
        daire_id: int, 
        giris_tarihi: Optional[datetime],
        cikis_tarihi: Optional[datetime],
        exclude_sakin_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> None:
        """
        Aynı dairede tarih çakışmasını kontrol et.
        
        Kurallar:
        1. cikis_tarihi > giris_tarihi (ayrılış > giriş)
        2. Dairede aktif (cikis_tarihi=None) sakin varsa hata
        3. Yeni sakin giriş tarihi > Eski sakin ayrılış tarihi
        
        Args:
            daire_id (int): Daire ID'si
            giris_tarihi (datetime, optional): Giriş tarihi
            cikis_tarihi (datetime, optional): Çıkış tarihi
            exclude_sakin_id (int, optional): Güncellemede hariç tutulacak sakin ID
            db (Session, optional): Veritabanı session
        
        Raises:
            ValidationError: Tarih çakışması veya kural ihlali
        
        Example:
            >>> controller._validate_daire_tarih_cakmasi(
            ...     daire_id=5,
            ...     giris_tarihi=datetime(2024, 1, 1),
            ...     cikis_tarihi=datetime(2024, 12, 31)
            ... )
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # Kural 1: cikis_tarihi > giris_tarihi
            if giris_tarihi and cikis_tarihi:
                if cikis_tarihi <= giris_tarihi:
                    raise ValidationError(
                        "Çıkış tarihi giriş tarihinden sonra olmalıdır.",
                        code="VAL_SAKN_001"
                    )
            
            # Kural 2 & 3: Aynı dairede sakinleri kontrol et
            # NOT: Pasif sakin yapıldığında daire_id=None, eski_daire_id set edilir
            # Bu yüzden hem daire_id hem eski_daire_id kontrol etmeli
            query = session.query(Sakin).filter(
                or_(
                    Sakin.daire_id == daire_id,          # Aktif sakin
                    Sakin.eski_daire_id == daire_id      # Pasif sakin
                ),
                Sakin.aktif == True  # Sadece aktif sakinleri kontrol et
            )
            
            if exclude_sakin_id:
                query = query.filter(Sakin.id != exclude_sakin_id)
            
            existing_sakinler = query.all()
            
            # Kural 2: Dairede aktif sakin varsa hata
            aktif_sakinler = [s for s in existing_sakinler if s.cikis_tarihi is None]
            if aktif_sakinler and giris_tarihi and cikis_tarihi is None:
                raise ValidationError(
                    f"Bu dairede zaten aktif sakin bulunmaktadır: {aktif_sakinler[0].ad_soyad}",
                    code="VAL_SAKN_002"
                )
            
            # Kural 3: Yeni sakin giriş > Eski sakin ayrılış
            if giris_tarihi:
                for existing in existing_sakinler:
                    if existing.cikis_tarihi:  # Pasif sakin
                        if giris_tarihi <= existing.cikis_tarihi:
                            raise ValidationError(
                                f"Yeni sakin giriş tarihi {existing.ad_soyad}'ın ayrılış tarihinden sonra olmalıdır "
                                f"({existing.cikis_tarihi.strftime('%d.%m.%Y')}).",
                                code="VAL_SAKN_003"
                            )
        
        finally:
            if close_db:
                session.close()
    
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
            
            # Tarih parsing (String → datetime)
            tahsis_tarihi = self._parse_date(data.get("tahsis_tarihi"))
            giris_tarihi = self._parse_date(data.get("giris_tarihi"))
            cikis_tarihi = self._parse_date(data.get("cikis_tarihi"))
            
            # Tarih çakışması validasyonu (HER ZAMAN çalışmalı)
            daire_id = data.get("daire_id")
            if daire_id and giris_tarihi:  # daire_id ve giris_tarihi zorunlu
                self._validate_daire_tarih_cakmasi(
                    daire_id=daire_id,
                    giris_tarihi=giris_tarihi,
                    cikis_tarihi=cikis_tarihi,
                    db=session
                )
            
            # Parsing sonrası tarih değerlerini güncelle
            if tahsis_tarihi is not None:
                data["tahsis_tarihi"] = tahsis_tarihi
            if giris_tarihi is not None:
                data["giris_tarihi"] = giris_tarihi
            if cikis_tarihi is not None:
                data["cikis_tarihi"] = cikis_tarihi
            
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
                - cikis_tarihi (str, optional): Çıkış tarihi (DD.MM.YYYY)
        
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
            
            # Tarih parsing (String → datetime)
            if "tahsis_tarihi" in data:
                data["tahsis_tarihi"] = self._parse_date(data.get("tahsis_tarihi"))
            if "giris_tarihi" in data:
                data["giris_tarihi"] = self._parse_date(data.get("giris_tarihi"))
            if "cikis_tarihi" in data:
                data["cikis_tarihi"] = self._parse_date(data.get("cikis_tarihi"))
            
            # Güncel sakin bilgisini al
            existing = session.query(Sakin).filter(Sakin.id == id).first()
            if existing:
                # Tarih çakışması validasyonu (daire_id ve giris_tarihi kontrol)
                giris_tarihi = data.get("giris_tarihi", existing.giris_tarihi)
                cikis_tarihi = data.get("cikis_tarihi", existing.cikis_tarihi)
                # Pasif sakinde daire_id=None ise eski_daire_id kullan
                daire_id = data.get("daire_id", existing.daire_id)
                if daire_id is None and existing.eski_daire_id is not None:
                    daire_id = existing.eski_daire_id
                
                # HER ZAMAN tarih çakışması validasyonu yapılmalı
                if daire_id and giris_tarihi:
                    self._validate_daire_tarih_cakmasi(
                        daire_id=daire_id,
                        giris_tarihi=giris_tarihi,
                        cikis_tarihi=cikis_tarihi,
                        exclude_sakin_id=id,  # Kendi kaydını hariç tut
                        db=session
                    )
            
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
