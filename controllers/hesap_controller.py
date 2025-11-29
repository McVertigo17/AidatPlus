"""
Hesap controller - Banka hesapları ve validasyonlar.

Bu modül, hesap yönetimi ve bakiye işlemlerini gerçekleştirir.
"""

from typing import List, Optional, cast
from sqlalchemy.orm import Session
from controllers.base_controller import BaseController
from models.base import Hesap
from models.validation import Validator
from models.exceptions import ValidationError
from database.config import get_db

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
        session = db or get_db()
        close_db = db is None
        
        try:
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
        
        except ValidationError:
            raise
        finally:
            if close_db:
                session.close()
    
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
        session = db or get_db()
        close_db = db is None
        
        try:
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
        
        except ValidationError:
            raise
        finally:
            if close_db:
                session.close()

    def get_aktif_hesaplar(self, db: Optional[Session] = None) -> List[Hesap]:
        """Aktif hesapları getir"""
        self.logger.debug("Fetching active accounts")
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            result = db.query(Hesap).filter(Hesap.aktif == True).all()
            self.logger.info(f"Successfully fetched {len(result)} active accounts")
            return cast(List[Hesap], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch active accounts: {str(e)}")
            raise
        finally:
            if close_db and db is not None:
                db.close()

    def get_pasif_hesaplar(self, db: Optional[Session] = None) -> List[Hesap]:
        """Pasif hesapları getir"""
        self.logger.debug("Fetching passive accounts")
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            result = db.query(Hesap).filter(Hesap.aktif == False).all()
            self.logger.info(f"Successfully fetched {len(result)} passive accounts")
            return cast(List[Hesap], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch passive accounts: {str(e)}")
            raise
        finally:
            if close_db and db is not None:
                db.close()

    def get_varsayilan_hesap(self, db: Optional[Session] = None) -> Optional[Hesap]:
        """Varsayılan hesabı getir"""
        self.logger.debug("Fetching default account")
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            result = db.query(Hesap).filter(
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
        finally:
            if close_db and db is not None:
                db.close()

    def set_varsayilan_hesap(self, hesap_id: int, db: Optional[Session] = None) -> bool:
        """Belirtilen hesabı varsayılan yap"""
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            # Önce tüm hesapların varsayılan flag'ini kaldır
            db.query(Hesap).update({"varsayilan": False})
            
            # Belirtilen hesabı varsayılan yap
            hesap = self.get_by_id(hesap_id, db)
            if hesap:
                hesap.varsayilan = True
                db.commit()
                return True
            return False
        finally:
            if close_db and db is not None:
                db.close()

    def hesap_bakiye_guncelle(self, hesap_id: int, tutar: float, islem_turu: str, db: Optional[Session] = None) -> bool:
        """Hesap bakiyesini güncelle (gelir/gider/transfer işlemine göre)"""
        self.logger.debug(f"Updating balance for account {hesap_id}: {islem_turu} {tutar}")
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            hesap = self.get_by_id(hesap_id, db)
            if hesap:
                old_balance = hesap.bakiye
                if islem_turu == "Gelir":
                    hesap.bakiye += tutar
                elif islem_turu == "Gider":
                    hesap.bakiye -= tutar
                # Transfer için özel işlem gerekmiyor çünkü transfer hem gelir hem gider olarak iki hesapta da işlenir

                db.commit()
                self.logger.info(f"Account {hesap_id} balance updated: {old_balance} → {hesap.bakiye}")
                return True
            self.logger.warning(f"Account {hesap_id} not found for balance update")
            return False
        except Exception as e:
            self.logger.error(f"Failed to update balance for account {hesap_id}: {str(e)}")
            raise
        finally:
            if close_db and db is not None:
                db.close()