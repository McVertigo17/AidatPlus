"""
Hesap controller - Banka hesapları ve validasyonlar.

Bu modül, hesap yönetimi ve bakiye işlemlerini gerçekleştirir.
"""

from typing import List, Optional, cast
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from controllers.base_controller import BaseController
from models.base import Hesap
from models.validation import Validator
from models.exceptions import ValidationError, DatabaseError
from database.config import get_db_session

# Logger import
from utils.logger import get_logger

class HesapController(BaseController[Hesap]):
    """
    Hesap yönetimi için controller.
    
    Banka hesapları, bakiyeler ve transfer işlemleri.
    
    Example:
        >>> controller = HesapController()
        >>> hesaplar = controller.get_aktif_hesaplar()
    """

    def __init__(self) -> None:
        super().__init__(Hesap)
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    def create(self, data: dict, db: Optional[Session] = None) -> Hesap:
        """
        Yeni hesap oluştur ve validasyon yap.
        
        Args:
            data (dict): Hesap verileri
                - ad (str): Hesap adı (2-100 karakter)
                - tur (str): Hesap tipi ("Banka", "Kasa", vb.)
                - bakiye (float): İlk bakiye (opsiyonel, default: 0)
        
        Returns:
            Hesap: Oluşturulan hesap
        
        Raises:
            ValidationError: Veri geçersiz ise
            DatabaseError: Veritabanı hatası
        
        Example:
            >>> data = {"ad": "Ziraat Bankası", "tipi": "Banka", "bakiye": 50000}
            >>> hesap = controller.create(data)
        """
        if db is not None:
            return self._execute_create(data, db)
        
        with get_db_session() as session:
            return self._execute_create(data, session)
    
    def _execute_create(self, data: dict, session: Session) -> Hesap:
        """Helper method to execute create logic"""
        # Hesap adı validasyonu
        Validator.validate_required(data.get("ad"), "Hesap Adı")
        Validator.validate_string_length(
            data.get("ad", ""), "Hesap Adı", 2, 100
        )
        
        # Hesap tipi validasyonu
        Validator.validate_required(data.get("tur"), "Hesap Tipi")
        Validator.validate_choice(
            data.get("tur"), "Hesap Tipi", ["Banka", "Kasa", "Cüzdan", "Tasarruf", "Diğer"]
        )
        
        # Bakiye validasyonu (opsiyonel, default: 0)
        if "bakiye" in data and data["bakiye"] is not None:
            Validator.validate_positive_number(
                data.get("bakiye", 0), "Bakiye", allow_zero=True
            )
            # Bakiye kuruş'a çevir (model property yerine doğrudan set et)
            bakiye_float = float(data["bakiye"])
            data["bakiye_kurus"] = int(round(bakiye_float * 100))
            del data["bakiye"]  # Eski anahtar silinsin
        else:
            data["bakiye_kurus"] = 0
            if "bakiye" in data:
                del data["bakiye"]
        
        # Base class'ın create metodunu çağır
        return super().create(data, session)
    
    def update(self, id: int, data: dict, db: Optional[Session] = None) -> Optional[Hesap]:
        """
        Hesap güncelle ve validasyon yap.
        
        Args:
            id (int): Hesap ID'si
            data (dict): Güncellenecek alanlar
        
        Returns:
            Hesap | None: Güncellenen hesap veya None
        
        Raises:
            ValidationError: Veri geçersiz ise
        """
        if db is not None:
            return self._execute_update(id, data, db)
        
        with get_db_session() as session:
            return self._execute_update(id, data, session)
    
    def _execute_update(self, id: int, data: dict, session: Session) -> Optional[Hesap]:
        """Helper method to execute update logic"""
        # Hesap adı validasyonu (eğer güncelleniyorsa)
        if "ad" in data and data["ad"]:
            Validator.validate_string_length(
                data["ad"], "Hesap Adı", 2, 100
            )
        
        # Hesap tipi validasyonu (eğer güncelleniyorsa)
        if "tur" in data and data["tur"]:
            Validator.validate_choice(
                data["tur"], "Hesap Tipi", ["Banka", "Kasa", "Cüzdan", "Tasarruf", "Diğer"]
            )
        
        # Bakiye validasyonu (eğer güncelleniyorsa)
        if "bakiye" in data and data["bakiye"] is not None:
            Validator.validate_positive_number(
                data["bakiye"], "Bakiye", allow_zero=True
            )
            # Bakiye kuruş'a çevir
            bakiye_float = float(data["bakiye"])
            data["bakiye_kurus"] = int(round(bakiye_float * 100))
            del data["bakiye"]  # Eski anahtar silinsin
        
        # Base class'ın update metodunu çağır
        return super().update(id, data, session)

    def get_aktif_hesaplar(self, db: Optional[Session] = None) -> List[Hesap]:
        """Aktif hesapları getir"""
        self.logger.debug("Fetching active accounts")
        
        if db is not None:
            result = db.query(Hesap).filter(Hesap.aktif == True).all()
            self.logger.info(f"Successfully fetched {len(result)} active accounts")
            return cast(List[Hesap], result)
        
        try:
            with get_db_session() as session:
                result = session.query(Hesap).filter(Hesap.aktif == True).all()
                self.logger.info(f"Successfully fetched {len(result)} active accounts")
                return cast(List[Hesap], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch active accounts: {str(e)}")
            raise

    def get_pasif_hesaplar(self, db: Optional[Session] = None) -> List[Hesap]:
        """Pasif hesapları getir"""
        self.logger.debug("Fetching passive accounts")
        
        if db is not None:
            result = db.query(Hesap).filter(Hesap.aktif == False).all()
            self.logger.info(f"Successfully fetched {len(result)} passive accounts")
            return cast(List[Hesap], result)
        
        try:
            with get_db_session() as session:
                result = session.query(Hesap).filter(Hesap.aktif == False).all()
                self.logger.info(f"Successfully fetched {len(result)} passive accounts")
                return cast(List[Hesap], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch passive accounts: {str(e)}")
            raise

    def get_varsayilan_hesap(self, db: Optional[Session] = None) -> Optional[Hesap]:
        """Varsayılan hesabı getir"""
        self.logger.debug("Fetching default account")
        
        if db is not None:
            result = db.query(Hesap).filter(
                Hesap.varsayilan == True,
                Hesap.aktif == True
            ).first()
            if result:
                self.logger.info(f"Default account found: {result.ad}")
            else:
                self.logger.warning("No default account found")
            return cast(Optional[Hesap], result)
        
        try:
            with get_db_session() as session:
                result = session.query(Hesap).filter(
                    Hesap.varsayilan == True,
                    Hesap.aktif == True
                ).first()
                if result:
                    self.logger.info(f"Default account found: {result.ad}")
                else:
                    self.logger.warning("No default account found")
                return cast(Optional[Hesap], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch default account: {str(e)}")
            raise

    def set_varsayilan_hesap(self, hesap_id: int, db: Optional[Session] = None) -> bool:
        """Belirtilen hesabı varsayılan yap"""
        if db is not None:
            # Önce tüm hesapların varsayılan flag'ini kaldır
            db.query(Hesap).update({"varsayilan": False})
            
            # Belirtilen hesabı varsayılan yap
            hesap = self.get_by_id(hesap_id, db)
            if hesap:
                hesap.varsayilan = True
                db.commit()
                return True
            return False
        
        with get_db_session() as session:
            # Önce tüm hesapların varsayılan flag'ini kaldır
            session.query(Hesap).update({"varsayilan": False})
            
            # Belirtilen hesabı varsayılan yap
            hesap = self.get_by_id(hesap_id, session)
            if hesap:
                hesap.varsayilan = True
                session.commit()
                return True
            return False

    def hesap_bakiye_guncelle(self, hesap_id: int, tutar: float, islem_turu: str, allow_negative: bool = False, db: Optional[Session] = None) -> bool:
        """
        Hesap bakiyesini güncelle (gelir/gider/transfer işlemine göre).
        
        Atomic transaction içinde gerçekleştirilir - kısmi güncellemeler engellenir.
        
        Args:
            hesap_id (int): Hesap ID'si
            tutar (float): İşlem tutarı (pozitif)
            islem_turu (str): İşlem türü ("Gelir", "Gider", "Transfer")
            db (Session, optional): Veritabanı session
        
        Returns:
            bool: True (başarılı), False (hesap bulunamadı)
        
        Raises:
            ValidationError: Bakiye negatif olacaksa (Gider türü)
            DatabaseError: Veritabanı hatası
        
        Example:
            >>> success = controller.hesap_bakiye_guncelle(1, 5000, "Gelir")
        """
        self.logger.debug(f"Updating balance for account {hesap_id}: {islem_turu} {tutar}")
        
        if db is not None:
            return self._execute_balance_update(hesap_id, tutar, islem_turu, allow_negative, db)
        
        with get_db_session() as session:
            return self._execute_balance_update(hesap_id, tutar, islem_turu, allow_negative, session)
    
    def _execute_balance_update(self, hesap_id: int, tutar: float, islem_turu: str, allow_negative: bool, session: Session) -> bool:
        """Helper method to execute balance update logic"""
        try:
            # Bakiye güncelleme türü validasyonu
            Validator.validate_choice(islem_turu, "İşlem Türü", ["Gelir", "Gider", "Transfer"])
            Validator.validate_positive_number(tutar, "Tutar")
            
            # Hesabı veritabanından kes (atomic update için row lock)
            hesap = session.query(Hesap).filter(Hesap.id == hesap_id).with_for_update().first()
            
            if not hesap:
                self.logger.warning(f"Account {hesap_id} not found for balance update")
                return False
            
            old_balance = hesap.bakiye
            
            # Yeni bakiye hesapla
            if islem_turu == "Gelir":
                new_balance = hesap.bakiye + tutar
            elif islem_turu == "Gider":
                new_balance = hesap.bakiye - tutar
                # Gider işleminde bakiye negatif olmasını kontrol et (allow_negative ile override edilebilir)
                if new_balance < 0 and not allow_negative:
                    raise ValidationError(
                        f"Yetersiz bakiye: {old_balance} TL < {tutar} TL",
                        code="VAL_ACC_001",
                        details={
                            "hesap_id": hesap_id,
                            "mevcut_bakiye": old_balance,
                            "istenen_tutar": tutar,
                            "fark": new_balance
                        }
                    )
            else:
                # Transfer tipinde bakiye işlemi direkt değişmez (gelir/gider olarak işlenir)
                return True
            
            # Bakiyeyi güncelle ve hemen commit et (transaction'ın içinde)
            hesap.bakiye = new_balance
            session.commit()
            
            self.logger.info(
                f"Account {hesap_id} balance updated: {old_balance} → {new_balance} "
                f"(Işlem: {islem_turu}, Tutar: {tutar})"
            )
            return True
            
        except ValidationError:
            session.rollback()
            raise
        except (IntegrityError, SQLAlchemyError) as e:
            session.rollback()
            self.logger.error(f"Database error updating balance for account {hesap_id}: {str(e)}")
            raise DatabaseError(
                f"Hesap bakiyesi güncellenirken veritabanı hatası: {str(e)}",
                code="DB_BAL_001",
                details={"hesap_id": hesap_id, "islem_turu": islem_turu}
            )
        except Exception as e:
            session.rollback()
            self.logger.error(f"Unexpected error updating balance for account {hesap_id}: {str(e)}")
            raise DatabaseError(
                f"Beklenmeyen hata: {str(e)}",
                code="DB_BAL_002",
                details={"hesap_id": hesap_id}
            )
