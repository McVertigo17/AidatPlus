"""
Finans işlem controller - Finans işlemleri ve validasyonlar.

Bu modül, gelir, gider ve transfer işlemlerini gerçekleştirir
ve hesap bakiyelerini yönetir.
"""

from typing import List, Optional, cast
from sqlalchemy.orm import Session, joinedload
from controllers.base_controller import BaseController
from models.base import FinansIslem, AltKategori, Hesap
from models.validation import Validator
from models.exceptions import ValidationError, NotFoundError
from database.config import get_db
from datetime import datetime
from controllers.hesap_controller import HesapController

# Logger import
from utils.logger import get_logger

class FinansIslemController(BaseController[FinansIslem]):
    """
    Finans işlemleri için controller.
    
    Gelir, gider ve transfer işlemlerini yönetir.
    Hesap bakiyelerini günceller.
    
    Example:
        >>> controller = FinansIslemController()
        >>> gelirler = controller.get_gelirler()
    """

    def __init__(self) -> None:
        super().__init__(FinansIslem)
        self.logger = get_logger(f"{self.__class__.__name__}")

    def create(self, data: dict, db: Optional[Session] = None) -> FinansIslem:
        """
        Yeni finans işlemi oluştur ve hesap bakiyesini güncelle.
        
        Args:
            data (dict): İşlem verileri
                - tur (str): İşlem türü ("Gelir", "Gider", "Transfer")
                - tutar (float): İşlem tutarı (pozitif)
                - hesap_id (int): Hesap ID'si
                - hedef_hesap_id (int, optional): Hedef hesap ID'si (Transfer için)
                - tarih (datetime): İşlem tarihi (zorunlu)
                - aciklama (str): Açıklama
                - kategori_id (int, optional): Kategori ID'si (opsiyonel)
        
        Returns:
            FinansIslem: Oluşturulan işlem nesnesi
        
        Raises:
            ValidationError: Veri geçersiz ise
            NotFoundError: Kategori bulunamadı ise
            DatabaseError: Veritabanı hatası
        
        Example:
            >>> data = {
            ...     "tur": "Gelir",
            ...     "tutar": 5000,
            ...     "hesap_id": 1,
            ...     "tarih": datetime.now(),
            ...     "aciklama": "Aidat geliri"
            ... }
            >>> islem = controller.create(data)
        """
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            # İşlem türü validasyonu
            Validator.validate_required(data.get("tur"), "İşlem Türü")
            Validator.validate_choice(
                data.get("tur"), "İşlem Türü", ["Gelir", "Gider", "Transfer"]
            )
            
            # Tutar validasyonu
            Validator.validate_required(data.get("tutar"), "Tutar")
            Validator.validate_positive_number(data.get("tutar"), "Tutar")
            
            # Hesap ID validasyonu
            Validator.validate_required(data.get("hesap_id"), "Hesap")
            Validator.validate_integer(data.get("hesap_id"), "Hesap ID")
            
            # Tarih validasyonu (zorunlu)
            Validator.validate_required(data.get("tarih"), "İşlem Tarihi")
            Validator.validate_date(data.get("tarih"))
            
            # Kategori ID validasyonu (opsiyonel)
            if data.get("kategori_id"):
                Validator.validate_integer(data.get("kategori_id"), "Kategori ID'si")
                Validator.validate_positive_number(data.get("kategori_id"), "Kategori ID'si")
                
                # Kategori var mı kontrol et
                kategori = db.query(AltKategori).filter(
                    AltKategori.id == data.get("kategori_id"),
                    AltKategori.aktif == True
                ).first()
                
                if not kategori:
                    raise NotFoundError(
                        f"Kategori ID {data.get('kategori_id')} bulunamadı",
                        code="NOT_FOUND_003",
                        details={"kategori_id": data.get("kategori_id")}
                    )
            
            # Transfer için hedef hesap validasyonu
            if data.get("tur") == "Transfer":
                Validator.validate_required(data.get("hedef_hesap_id"), "Hedef Hesap")
                Validator.validate_integer(data.get("hedef_hesap_id"), "Hedef Hesap ID")
            
            # İşlemi oluştur
            islem = FinansIslem(**data)
            db.add(islem)
            db.commit()
            db.refresh(islem)
            
            # Bakiyeleri güncelle
            hesap_controller = HesapController()
            islem_tur = data.get("tur", "")
            
            if islem_tur == "Transfer":
                # Transfer için her iki hesabı güncelle
                if data.get("hesap_id"):
                    hesap_controller.hesap_bakiye_guncelle(int(data.get("hesap_id", 0)), data.get("tutar", 0), "Gider", db)
                if data.get("hedef_hesap_id"):
                    hesap_controller.hesap_bakiye_guncelle(int(data.get("hedef_hesap_id", 0)), data.get("tutar", 0), "Gelir", db)
            else:
                # Gelir/Gider işlemleri
                if data.get("hesap_id"):
                    hesap_controller.hesap_bakiye_guncelle(int(data.get("hesap_id", 0)), data.get("tutar", 0), islem_tur, db)
            
            return islem
        
        except (ValidationError, NotFoundError):
            raise
        finally:
            if close_db and db is not None:
                db.close()

    def get_gelirler(self, db: Optional[Session] = None) -> List[FinansIslem]:
        """Gelir işlemlerini getir"""
        self.logger.debug("Fetching income transactions")
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            result = db.query(FinansIslem).options(
                joinedload(FinansIslem.hesap),
                joinedload(FinansIslem.hedef_hesap),
                joinedload(FinansIslem.kategori).joinedload(AltKategori.ana_kategori)
            ).filter(
                FinansIslem.tur == "Gelir",
                FinansIslem.aktif == True
            ).order_by(FinansIslem.tarih.desc()).all()
            self.logger.info(f"Successfully fetched {len(result)} income transactions")
            return cast(List[FinansIslem], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch income transactions: {str(e)}")
            raise
        finally:
            if close_db and db is not None:
                db.close()

    def get_giderler(self, db: Optional[Session] = None) -> List[FinansIslem]:
        """Gider işlemlerini getir"""
        self.logger.debug("Fetching expense transactions")
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            result = db.query(FinansIslem).options(
                joinedload(FinansIslem.hesap),
                joinedload(FinansIslem.hedef_hesap),
                joinedload(FinansIslem.kategori).joinedload(AltKategori.ana_kategori)
            ).filter(
                FinansIslem.tur == "Gider",
                FinansIslem.aktif == True
            ).order_by(FinansIslem.tarih.desc()).all()
            self.logger.info(f"Successfully fetched {len(result)} expense transactions")
            return cast(List[FinansIslem], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch expense transactions: {str(e)}")
            raise
        finally:
            if close_db and db is not None:
                db.close()

    def get_transferler(self, db: Optional[Session] = None) -> List[FinansIslem]:
        """Transfer işlemlerini getir"""
        self.logger.debug("Fetching transfer transactions")
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            result = db.query(FinansIslem).options(
                joinedload(FinansIslem.hesap),
                joinedload(FinansIslem.hedef_hesap)
            ).filter(
                FinansIslem.tur == "Transfer",
                FinansIslem.aktif == True
            ).order_by(FinansIslem.tarih.desc()).all()
            self.logger.info(f"Successfully fetched {len(result)} transfer transactions")
            return cast(List[FinansIslem], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch transfer transactions: {str(e)}")
            raise
        finally:
            if close_db and db is not None:
                db.close()

    def get_by_hesap(self, hesap_id: int, db: Optional[Session] = None) -> List[FinansIslem]:
        """Hesaba göre işlemleri getir"""
        self.logger.debug(f"Fetching transactions for account {hesap_id}")
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            result = db.query(FinansIslem).options(
                joinedload(FinansIslem.kategori)
            ).filter(
                FinansIslem.hesap_id == hesap_id,
                FinansIslem.aktif == True
            ).order_by(FinansIslem.tarih.desc()).all()
            self.logger.info(f"Successfully fetched {len(result)} transactions for account {hesap_id}")
            return cast(List[FinansIslem], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch transactions for account {hesap_id}: {str(e)}")
            raise
        finally:
            if close_db and db is not None:
                db.close()

    def get_by_kategori(self, kategori_id: int, db: Optional[Session] = None) -> List[FinansIslem]:
        """Kategoriye göre işlemleri getir"""
        self.logger.debug(f"Fetching transactions for category {kategori_id}")
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            result = db.query(FinansIslem).options(
                joinedload(FinansIslem.hesap)
            ).filter(
                FinansIslem.kategori_id == kategori_id,
                FinansIslem.aktif == True
            ).order_by(FinansIslem.tarih.desc()).all()
            self.logger.info(f"Successfully fetched {len(result)} transactions for category {kategori_id}")
            return cast(List[FinansIslem], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch transactions for category {kategori_id}: {str(e)}")
            raise
        finally:
            if close_db and db is not None:
                db.close()

    def get_by_tarih_araligi(self, baslangic_tarihi: datetime, bitis_tarihi: datetime, db: Optional[Session] = None) -> List[FinansIslem]:
        """Tarih aralığına göre işlemleri getir"""
        self.logger.debug(f"Fetching transactions between {baslangic_tarihi} and {bitis_tarihi}")
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            result = db.query(FinansIslem).options(
                joinedload(FinansIslem.hesap),
                joinedload(FinansIslem.kategori)
            ).filter(
                FinansIslem.tarih.between(baslangic_tarihi, bitis_tarihi),
                FinansIslem.aktif == True
            ).order_by(FinansIslem.tarih.desc()).all()
            self.logger.info(f"Successfully fetched {len(result)} transactions in date range")
            return cast(List[FinansIslem], result)
        except Exception as e:
            self.logger.error(f"Failed to fetch transactions in date range: {str(e)}")
            raise
        finally:
            if close_db and db is not None:
                db.close()

    def update_with_balance_adjustment(self, id: int, data: dict, db: Optional[Session] = None) -> Optional[FinansIslem]:
        """Kayıt güncelle ve hesap bakiyelerini uygun şekilde ayarla"""
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            # Önce mevcut işlemi veritabanından al
            # We need to query directly to ensure the object is bound to the current session
            existing_islem: Optional[FinansIslem] = db.query(FinansIslem).filter(FinansIslem.id == id).first()
            
            if existing_islem:
                # Mevcut işlem verilerini sakla
                old_tutar = existing_islem.tutar
                old_tur = existing_islem.tur
                old_hesap_id = existing_islem.hesap_id
                old_hedef_hesap_id = existing_islem.hedef_hesap_id
                
                # Yeni verileri güncelle
                for key, value in data.items():
                    setattr(existing_islem, key, value)
                
                db.commit()
                db.refresh(existing_islem)
                
                # Hesap bakiyelerini güncelle
                new_tutar = data.get('tutar', old_tutar)
                new_tur = data.get('tur', old_tur)
                new_hesap_id = data.get('hesap_id', old_hesap_id)
                new_hedef_hesap_id = data.get('hedef_hesap_id', old_hedef_hesap_id)
                
                hesap_controller = HesapController()
                
                # Transfer işlemleri için
                if old_tur == "Transfer" or new_tur == "Transfer":
                    # Eski transferi geri al
                    if old_tur == "Transfer":
                        # Kaynak hesaptan çıkan parayı geri ekle
                        if old_hesap_id is not None:
                            hesap_controller.hesap_bakiye_guncelle(old_hesap_id, old_tutar, "Gelir", db)
                        # Hedef hesaba gelen parayı geri çıkar
                        if old_hedef_hesap_id is not None:
                            hesap_controller.hesap_bakiye_guncelle(old_hedef_hesap_id, old_tutar, "Gider", db)
                    
                    # Yeni transferi uygula
                    if new_tur == "Transfer":
                        # Kaynak hesaptan para çıkart
                        if new_hesap_id is not None:
                            hesap_controller.hesap_bakiye_guncelle(new_hesap_id, new_tutar, "Gider", db)
                        # Hedef hesaba para ekle
                        if new_hedef_hesap_id is not None:
                            hesap_controller.hesap_bakiye_guncelle(new_hedef_hesap_id, new_tutar, "Gelir", db)
                else:
                    # Normal gelir/gider işlemleri
                    # Eski işlemi geri al
                    if old_hesap_id is not None:
                        if old_tur == "Gelir":
                            hesap_controller.hesap_bakiye_guncelle(old_hesap_id, old_tutar, "Gider", db)
                        else:  # Gider
                            hesap_controller.hesap_bakiye_guncelle(old_hesap_id, old_tutar, "Gelir", db)
                    
                    # Yeni işlemi uygula
                    if new_hesap_id is not None:
                        if new_tur == "Gelir":
                            hesap_controller.hesap_bakiye_guncelle(new_hesap_id, new_tutar, "Gelir", db)
                        else:  # Gider
                            hesap_controller.hesap_bakiye_guncelle(new_hesap_id, new_tutar, "Gider", db)
                
                return existing_islem
            return None
        finally:
            if close_db and db is not None:
                db.close()

    def delete(self, id: int, db: Optional[Session] = None) -> bool:
        """Kayıt sil ve transfer işlemleri için bakiyeleri güncelle"""
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            # Önce işlemi veritabanından al
            # We need to query directly to ensure the object is bound to the current session
            islem: Optional[FinansIslem] = db.query(FinansIslem).filter(FinansIslem.id == id).first()
            
            if islem:
                # Hesap controller'ı oluştur
                hesap_controller = HesapController()
                
                # İşlem türüne göre bakiyeleri geri al
                if islem.tur == "Transfer":
                    # Kaynak hesaptan çıkan parayı geri ekle (Gelir gibi)
                    if islem.hesap_id is not None:
                        hesap_controller.hesap_bakiye_guncelle(islem.hesap_id, islem.tutar, "Gelir", db)
                    
                    # Hedef hesaba gelen parayı geri çıkar (Gider gibi)
                    if islem.hedef_hesap_id is not None:
                        hesap_controller.hesap_bakiye_guncelle(islem.hedef_hesap_id, islem.tutar, "Gider", db)
                elif islem.tur == "Gelir":
                    # Gelir işlemi silinirse, hesaptan parayı çıkar
                    if islem.hesap_id is not None:
                        hesap_controller.hesap_bakiye_guncelle(islem.hesap_id, islem.tutar, "Gider", db)
                elif islem.tur == "Gider":
                    # Gider işlemi silinirse, hesaba parayı geri ekle
                    if islem.hesap_id is not None:
                        hesap_controller.hesap_bakiye_guncelle(islem.hesap_id, islem.tutar, "Gelir", db)
                
                # İşlemi sil
                db.delete(islem)
                db.commit()
                return True
            return False
        finally:
            if close_db and db is not None:
                db.close()