"""
Finans işlem controller - Finans işlemleri ve validasyonlar.

Bu modül, gelir, gider ve transfer işlemlerini gerçekleştirir
ve hesap bakiyelerini yönetir.
"""

from typing import List, Optional, cast
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from controllers.base_controller import BaseController
from models.base import FinansIslem, AltKategori, Hesap
from models.validation import Validator
from models.exceptions import ValidationError, NotFoundError, DatabaseError
from database.config import get_db_session, get_db
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

    def create(self, data: dict, db: Session = None) -> FinansIslem:
        """
        Yeni finans işlemi oluştur ve hesap bakiyesini güncelle (ATOMIC).
        
        İşlem ve hesap bakiyeleri aynı transaction'da güncellenir.
        Herhangi bir hata durumunda tüm değişiklikler geri alınır.
        
        Args:
            data (dict): İşlem verileri
                - tur (str): İşlem türü ("Gelir", "Gider", "Transfer")
                - tutar (float): İşlem tutarı (pozitif)
                - hesap_id (int): Hesap ID'si
                - hedef_hesap_id (int, optional): Hedef hesap ID'si (Transfer için)
                - tarih (datetime): İşlem tarihi (zorunlu)
                - aciklama (str): Açıklama
                - kategori_id (int, optional): Kategori ID'si (opsiyonel)
            db (Session, optional): Veritabanı session
        
        Returns:
            FinansIslem: Oluşturulan işlem nesnesi
        
        Raises:
            ValidationError: Veri geçersiz ise veya yetersiz bakiye
            NotFoundError: Kategori veya hesap bulunamadı ise
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
        session = db or get_db()
        close_db = db is None
        
        try:
            # 1. VALIDASYON AŞAMASI (DB işlemi olmadan yapılır)
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
            
            islem_tur = data.get("tur", "")
            hesap_id = int(data.get("hesap_id", 0))
            tutar = float(data.get("tutar", 0))
            
            # Hedef hesap validasyonu (Transfer için)
            hedef_hesap_id = None
            if islem_tur == "Transfer":
                Validator.validate_required(data.get("hedef_hesap_id"), "Hedef Hesap")
                Validator.validate_integer(data.get("hedef_hesap_id"), "Hedef Hesap ID")
                hedef_hesap_id = int(data.get("hedef_hesap_id", 0))
                
                # Aynı hesaba transfer kontrolü
                if hesap_id == hedef_hesap_id:
                    raise ValidationError(
                        "Kaynak ve hedef hesap aynı olamaz",
                        code="VAL_TRN_001",
                        details={"hesap_id": hesap_id, "hedef_hesap_id": hedef_hesap_id}
                    )
            
            # Kategori ID validasyonu (opsiyonel)
            if data.get("kategori_id"):
                Validator.validate_integer(data.get("kategori_id"), "Kategori ID'si")
                Validator.validate_positive_number(data.get("kategori_id"), "Kategori ID'si")
                
                # Kategori var mı kontrol et (kategori_id ön kontrol)
                kategori = session.query(AltKategori).filter(
                    AltKategori.id == data.get("kategori_id"),
                    AltKategori.aktif == True
                ).first()
                
                if not kategori:
                    raise NotFoundError(
                        f"Kategori ID {data.get('kategori_id')} bulunamadı",
                        code="NOT_FOUND_003",
                        details={"kategori_id": data.get("kategori_id")}
                    )
            
            # 2. HESAP KONTROLÜ (Row lock ile atomic işlem için)
            hesap = session.query(Hesap).filter(Hesap.id == hesap_id).with_for_update().first()
            if not hesap:
                raise NotFoundError(
                    f"Hesap ID {hesap_id} bulunamadı",
                    code="NOT_FOUND_ACC_001",
                    details={"hesap_id": hesap_id}
                )
            
            hedef_hesap = None
            if hedef_hesap_id:
                hedef_hesap = session.query(Hesap).filter(Hesap.id == hedef_hesap_id).with_for_update().first()
                if not hedef_hesap:
                    raise NotFoundError(
                        f"Hedef hesap ID {hedef_hesap_id} bulunamadı",
                        code="NOT_FOUND_ACC_002",
                        details={"hedef_hesap_id": hedef_hesap_id}
                    )
            
            # 3. BAKIYE PRE-KONTROLÜ (Atomic transaction başlamadan önce)
            if islem_tur == "Gider":
                if hesap.bakiye < tutar:
                    raise ValidationError(
                        f"Yetersiz bakiye: {hesap.bakiye} TL < {tutar} TL",
                        code="VAL_ACC_001",
                        details={
                            "hesap_id": hesap_id,
                            "mevcut_bakiye": hesap.bakiye,
                            "istenen_tutar": tutar
                        }
                    )
            elif islem_tur == "Transfer":
                if hesap.bakiye < tutar:
                    raise ValidationError(
                        f"Transfer için yetersiz bakiye: {hesap.bakiye} TL < {tutar} TL",
                        code="VAL_TRN_002",
                        details={
                            "hesap_id": hesap_id,
                            "mevcut_bakiye": hesap.bakiye,
                            "transfer_tutari": tutar
                        }
                    )
            
            # 4. ATOMIC TRANSACTION (İşlem + Bakiye güncelleme)
            # İşlemi oluştur
            islem = FinansIslem(**data)
            session.add(islem)
            session.flush()  # DB'ye yazıyoruz ama commit etmiyoruz
            
            # Bakiyeleri güncelle (aynı transaction'ın içinde)
            try:
                if islem_tur == "Transfer":
                    # Transfer: Kaynak hesaptan çıkar, hedef hesaba ekle
                    hesap.bakiye -= tutar
                    if hedef_hesap:
                        hedef_hesap.bakiye += tutar
                    
                    self.logger.debug(
                        f"Transfer atomic update: {hesap_id} (-{tutar}) → {hedef_hesap_id} (+{tutar})"
                    )
                else:
                    # Gelir/Gider: Tek hesabı güncelle
                    if islem_tur == "Gelir":
                        hesap.bakiye += tutar
                    elif islem_tur == "Gider":
                        hesap.bakiye -= tutar
                    
                    self.logger.debug(f"{islem_tur} atomic update: {hesap_id} ({'+' if islem_tur == 'Gelir' else '-'}{tutar})")
                
                # Tüm değişiklikleri commit et (ATOMIC)
                session.commit()
                session.refresh(islem)
                
                self.logger.info(
                    f"Finance transaction created (ID: {islem.id}, Type: {islem_tur}, "
                    f"Amount: {tutar}, Account: {hesap_id})"
                )
                return islem
            
            except (IntegrityError, SQLAlchemyError) as e:
                session.rollback()
                self.logger.error(f"Atomic transaction failed during balance update: {str(e)}")
                raise DatabaseError(
                    f"İşlem ve bakiye güncellemesi başarısız (atomic transaction): {str(e)}",
                    code="DB_TRN_001",
                    details={
                        "islem_turu": islem_tur,
                        "hesap_id": hesap_id,
                        "tutar": tutar
                    }
                )
        
        except (ValidationError, NotFoundError, DatabaseError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during create: {str(e)}")
            raise DatabaseError(
                f"Beklenmeyen hata: {str(e)}",
                code="DB_001",
                details={"error_type": type(e).__name__}
            )
        finally:
            if close_db:
                session.close()

    def get_gelirler(self, db: Session = None) -> List[FinansIslem]:
        """
        Gelir işlemlerini getir.
        
        Args:
            db (Session, optional): Veritabanı session
        
        Returns:
            List[FinansIslem]: Gelir işlemleri listesi
        """
        self.logger.debug("Fetching income transactions")
        session = db or get_db()
        close_db = db is None
        
        try:
            result = session.query(FinansIslem).options(
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
            if close_db:
                session.close()

    def get_giderler(self, db: Session = None) -> List[FinansIslem]:
        """
        Gider işlemlerini getir.
        
        Args:
            db (Session, optional): Veritabanı session
        
        Returns:
            List[FinansIslem]: Gider işlemleri listesi
        """
        self.logger.debug("Fetching expense transactions")
        session = db or get_db()
        close_db = db is None
        
        try:
            result = session.query(FinansIslem).options(
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
            if close_db:
                session.close()

    def get_transferler(self, db: Session = None) -> List[FinansIslem]:
        """
        Transfer işlemlerini getir.
        
        Args:
            db (Session, optional): Veritabanı session
        
        Returns:
            List[FinansIslem]: Transfer işlemleri listesi
        """
        self.logger.debug("Fetching transfer transactions")
        session = db or get_db()
        close_db = db is None
        
        try:
            result = session.query(FinansIslem).options(
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
            if close_db:
                session.close()

    def get_by_hesap(self, hesap_id: int, db: Session = None) -> List[FinansIslem]:
        """
        Hesaba göre işlemleri getir.
        
        Args:
            hesap_id (int): Hesap ID'si
            db (Session, optional): Veritabanı session
        
        Returns:
            List[FinansIslem]: Hesaba ait işlemler
        """
        self.logger.debug(f"Fetching transactions for account {hesap_id}")
        session = db or get_db()
        close_db = db is None
        
        try:
            result = session.query(FinansIslem).options(
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
            if close_db:
                session.close()

    def get_by_kategori(self, kategori_id: int, db: Session = None) -> List[FinansIslem]:
        """
        Kategoriye göre işlemleri getir.
        
        Args:
            kategori_id (int): Kategori ID'si
            db (Session, optional): Veritabanı session
        
        Returns:
            List[FinansIslem]: Kategori işlemleri
        """
        self.logger.debug(f"Fetching transactions for category {kategori_id}")
        session = db or get_db()
        close_db = db is None
        
        try:
            result = session.query(FinansIslem).options(
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
            if close_db:
                session.close()

    def get_by_tarih_araligi(self, baslangic_tarihi: datetime, bitis_tarihi: datetime, db: Session = None) -> List[FinansIslem]:
        """
        Tarih aralığına göre işlemleri getir.
        
        Args:
            baslangic_tarihi (datetime): Başlangıç tarihi
            bitis_tarihi (datetime): Bitiş tarihi
            db (Session, optional): Veritabanı session
        
        Returns:
            List[FinansIslem]: Tarih aralığındaki işlemler
        """
        self.logger.debug(f"Fetching transactions between {baslangic_tarihi} and {bitis_tarihi}")
        session = db or get_db()
        close_db = db is None
        
        try:
            result = session.query(FinansIslem).options(
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
            if close_db:
                session.close()

    def update_with_balance_adjustment(self, id: int, data: dict, db: Session = None) -> Optional[FinansIslem]:
        """
        Kayıt güncelle ve hesap bakiyelerini uygun şekilde ayarla (ATOMIC).
        
        Eski işlem bakiyeleri geri alınır, yeni işlem bakiyeleri uygulanır.
        Tüm işlemler aynı transaction'da gerçekleştirilir.
        
        Args:
            id (int): Güncellenecek işlem ID'si
            data (dict): Yeni işlem verileri (tur, tutar, hesap_id, hedef_hesap_id, vb.)
            db (Session, optional): Veritabanı session
        
        Returns:
            FinansIslem | None: Güncellenen işlem veya None (bulunamadı)
        
        Raises:
            ValidationError: Veri geçersiz ise veya yetersiz bakiye
            NotFoundError: İşlem veya hesap bulunamadı ise
            DatabaseError: Veritabanı hatası
        
        Example:
            >>> data = {"tur": "Gider", "tutar": 3000}
            >>> islem = controller.update_with_balance_adjustment(42, data)
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # 1. VALIDASYON: Yeni verileri kontrol et
            if 'tur' in data:
                Validator.validate_choice(data['tur'], "İşlem Türü", ["Gelir", "Gider", "Transfer"])
            
            if 'tutar' in data:
                Validator.validate_positive_number(data['tutar'], "Tutar")
            
            if 'hesap_id' in data:
                Validator.validate_integer(data['hesap_id'], "Hesap ID")
            
            if 'hedef_hesap_id' in data and data.get('tur') == 'Transfer':
                Validator.validate_integer(data['hedef_hesap_id'], "Hedef Hesap ID")
            
            # 2. İşlemi veritabanından al (row lock ile)
            existing_islem: Optional[FinansIslem] = session.query(FinansIslem).filter(
                FinansIslem.id == id
            ).with_for_update().first()
            
            if not existing_islem:
                self.logger.warning(f"Finance transaction {id} not found for update")
                return None
            
            # Eski değerleri sakla
            old_tutar = existing_islem.tutar
            old_tur = existing_islem.tur
            old_hesap_id = existing_islem.hesap_id
            old_hedef_hesap_id = existing_islem.hedef_hesap_id
            
            # Yeni değerleri belirle
            new_tutar = data.get('tutar', old_tutar)
            new_tur = data.get('tur', old_tur)
            new_hesap_id = data.get('hesap_id', old_hesap_id)
            new_hedef_hesap_id = data.get('hedef_hesap_id', old_hedef_hesap_id)
            
            # Transfer tip değişikliğinde hedef hesap kontrolü
            if new_tur == "Transfer" and old_tur != "Transfer":
                if new_hesap_id == new_hedef_hesap_id:
                    raise ValidationError(
                        "Kaynak ve hedef hesap aynı olamaz",
                        code="VAL_TRN_001",
                        details={"hesap_id": new_hesap_id, "hedef_hesap_id": new_hedef_hesap_id}
                    )
            
            # 3. HESAP KONTROLÜ VE LOCK (Row lock ile atomic işlem için)
            hesaplar = {}
            
            # Eski hesapları lock al
            if old_hesap_id:
                hesaplar['old_hesap'] = session.query(Hesap).filter(
                    Hesap.id == old_hesap_id
                ).with_for_update().first()
                if not hesaplar['old_hesap']:
                    raise NotFoundError(
                        f"Eski hesap ID {old_hesap_id} bulunamadı",
                        code="NOT_FOUND_ACC_001",
                        details={"hesap_id": old_hesap_id}
                    )
            
            if old_hedef_hesap_id:
                hesaplar['old_hedef_hesap'] = session.query(Hesap).filter(
                    Hesap.id == old_hedef_hesap_id
                ).with_for_update().first()
                if not hesaplar['old_hedef_hesap']:
                    raise NotFoundError(
                        f"Eski hedef hesap ID {old_hedef_hesap_id} bulunamadı",
                        code="NOT_FOUND_ACC_002",
                        details={"hedef_hesap_id": old_hedef_hesap_id}
                    )
            
            # Yeni hesapları lock al
            if new_hesap_id:
                hesaplar['new_hesap'] = session.query(Hesap).filter(
                    Hesap.id == new_hesap_id
                ).with_for_update().first()
                if not hesaplar['new_hesap']:
                    raise NotFoundError(
                        f"Yeni hesap ID {new_hesap_id} bulunamadı",
                        code="NOT_FOUND_ACC_001",
                        details={"hesap_id": new_hesap_id}
                    )
            
            if new_hedef_hesap_id:
                hesaplar['new_hedef_hesap'] = session.query(Hesap).filter(
                    Hesap.id == new_hedef_hesap_id
                ).with_for_update().first()
                if not hesaplar['new_hedef_hesap']:
                    raise NotFoundError(
                        f"Yeni hedef hesap ID {new_hedef_hesap_id} bulunamadı",
                        code="NOT_FOUND_ACC_002",
                        details={"hedef_hesap_id": new_hedef_hesap_id}
                    )
            
            # 4. BAKIYE PRE-KONTROLÜ
            # Yeni işlem için bakiye kontrolü
            if new_tur == "Gider":
                yeni_hesap = hesaplar.get('new_hesap', hesaplar.get('old_hesap'))
                if yeni_hesap and (yeni_hesap.bakiye < new_tutar):
                    raise ValidationError(
                        f"Yetersiz bakiye: {yeni_hesap.bakiye} TL < {new_tutar} TL",
                        code="VAL_ACC_001",
                        details={
                            "hesap_id": new_hesap_id,
                            "mevcut_bakiye": yeni_hesap.bakiye,
                            "istenen_tutar": new_tutar
                        }
                    )
            elif new_tur == "Transfer":
                yeni_hesap = hesaplar.get('new_hesap', hesaplar.get('old_hesap'))
                if yeni_hesap and (yeni_hesap.bakiye < new_tutar):
                    raise ValidationError(
                        f"Transfer için yetersiz bakiye: {yeni_hesap.bakiye} TL < {new_tutar} TL",
                        code="VAL_TRN_002",
                        details={
                            "hesap_id": new_hesap_id,
                            "mevcut_bakiye": yeni_hesap.bakiye,
                            "transfer_tutari": new_tutar
                        }
                    )
            
            # 5. ATOMIC TRANSACTION (Bakiye düzeltmeleri + Güncelleme)
            try:
                # Eski işlemi geri al
                if old_tur == "Transfer":
                    if hesaplar.get('old_hesap'):
                        hesaplar['old_hesap'].bakiye += old_tutar
                    if hesaplar.get('old_hedef_hesap'):
                        hesaplar['old_hedef_hesap'].bakiye -= old_tutar
                    
                    self.logger.debug(f"Reverse old transfer: {old_hesap_id} (+{old_tutar}) ← {old_hedef_hesap_id}")
                
                elif old_tur == "Gelir":
                    if hesaplar.get('old_hesap'):
                        hesaplar['old_hesap'].bakiye -= old_tutar
                    
                    self.logger.debug(f"Reverse old income: {old_hesap_id} (-{old_tutar})")
                
                elif old_tur == "Gider":
                    if hesaplar.get('old_hesap'):
                        hesaplar['old_hesap'].bakiye += old_tutar
                    
                    self.logger.debug(f"Reverse old expense: {old_hesap_id} (+{old_tutar})")
                
                # Yeni işlemi uygula
                if new_tur == "Transfer":
                    if hesaplar.get('new_hesap'):
                        hesaplar['new_hesap'].bakiye -= new_tutar
                    if hesaplar.get('new_hedef_hesap'):
                        hesaplar['new_hedef_hesap'].bakiye += new_tutar
                    
                    self.logger.debug(f"Apply new transfer: {new_hesap_id} (-{new_tutar}) → {new_hedef_hesap_id}")
                
                elif new_tur == "Gelir":
                    if hesaplar.get('new_hesap'):
                        hesaplar['new_hesap'].bakiye += new_tutar
                    
                    self.logger.debug(f"Apply new income: {new_hesap_id} (+{new_tutar})")
                
                elif new_tur == "Gider":
                    if hesaplar.get('new_hesap'):
                        hesaplar['new_hesap'].bakiye -= new_tutar
                    
                    self.logger.debug(f"Apply new expense: {new_hesap_id} (-{new_tutar})")
                
                # İşlem kaydını güncelle
                for key, value in data.items():
                    if hasattr(existing_islem, key):
                        setattr(existing_islem, key, value)
                
                # Tüm değişiklikleri commit et (ATOMIC)
                session.commit()
                session.refresh(existing_islem)
                
                self.logger.info(
                    f"Finance transaction updated (ID: {id}, "
                    f"Type: {old_tur}→{new_tur}, Amount: {old_tutar}→{new_tutar})"
                )
                return existing_islem
            
            except (IntegrityError, SQLAlchemyError) as e:
                session.rollback()
                self.logger.error(f"Atomic transaction failed during update: {str(e)}")
                raise DatabaseError(
                    f"İşlem güncelleme ve bakiye düzeltmesi başarısız (atomic transaction): {str(e)}",
                    code="DB_UPD_001",
                    details={
                        "islem_id": id,
                        "old_tur": old_tur,
                        "new_tur": new_tur
                    }
                )
        
        except (ValidationError, NotFoundError, DatabaseError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during update: {str(e)}")
            raise DatabaseError(
                f"Beklenmeyen hata: {str(e)}",
                code="DB_001",
                details={"error_type": type(e).__name__}
            )
        finally:
            if close_db:
                session.close()

    def delete(self, id: int, db: Session = None) -> bool:
        """
        İşlemi sil ve hesap bakiyelerini geri al (ATOMIC).
        
        İşlem silme ve bakiye düzeltmeleri aynı transaction'da yapılır.
        Herhangi bir hata durumunda tüm değişiklikler geri alınır.
        
        Args:
            id (int): Silinecek işlem ID'si
            db (Session, optional): Veritabanı session
        
        Returns:
            bool: True (başarılı), False (işlem bulunamadı)
        
        Raises:
            DatabaseError: Veritabanı hatası
        
        Example:
            >>> success = controller.delete(42)
        """
        session = db or get_db()
        close_db = db is None
        
        try:
            # 1. İşlemi veritabanından al (row lock ile atomic işlem için)
            islem: Optional[FinansIslem] = session.query(FinansIslem).filter(
                FinansIslem.id == id
            ).with_for_update().first()
            
            if not islem:
                self.logger.warning(f"Finance transaction {id} not found for deletion")
                return False
            
            # Silme öncesi log için veri sakla
            islem_tur = islem.tur
            hesap_id = islem.hesap_id
            hedef_hesap_id = islem.hedef_hesap_id
            tutar = islem.tutar
            
            # 2. ATOMIC TRANSACTION (Bakiye düzeltmeleri)
            try:
                # Hesapları lock al
                hesap = None
                if hesap_id:
                    hesap = session.query(Hesap).filter(Hesap.id == hesap_id).with_for_update().first()
                    if not hesap:
                        raise NotFoundError(
                            f"Hesap ID {hesap_id} bulunamadı",
                            code="NOT_FOUND_ACC_001",
                            details={"hesap_id": hesap_id}
                        )
                
                hedef_hesap = None
                if hedef_hesap_id:
                    hedef_hesap = session.query(Hesap).filter(Hesap.id == hedef_hesap_id).with_for_update().first()
                    if not hedef_hesap:
                        raise NotFoundError(
                            f"Hedef hesap ID {hedef_hesap_id} bulunamadı",
                            code="NOT_FOUND_ACC_002",
                            details={"hedef_hesap_id": hedef_hesap_id}
                        )
                
                # Bakiyeleri geri al (işlem türüne göre)
                if islem_tur == "Transfer":
                    # Transfer işlemini geri al:
                    # - Kaynak hesaptan çıkan parayı geri ekle
                    # - Hedef hesaba gelen parayı geri çıkar
                    if hesap:
                        hesap.bakiye += tutar
                    if hedef_hesap:
                        hedef_hesap.bakiye -= tutar
                    
                    self.logger.debug(f"Transfer reversal: {hesap_id} (+{tutar}) ← {hedef_hesap_id} (-{tutar})")
                    
                elif islem_tur == "Gelir":
                    # Gelir işlemi silinirse, hesaptan parayı çıkar
                    if hesap:
                        hesap.bakiye -= tutar
                    
                    self.logger.debug(f"Income reversal: {hesap_id} (-{tutar})")
                    
                elif islem_tur == "Gider":
                    # Gider işlemi silinirse, hesaba parayı geri ekle
                    if hesap:
                        hesap.bakiye += tutar
                    
                    self.logger.debug(f"Expense reversal: {hesap_id} (+{tutar})")
                
                # İşlemi sil
                session.delete(islem)
                
                # Tüm değişiklikleri commit et (ATOMIC)
                session.commit()
                
                self.logger.info(
                    f"Finance transaction deleted (ID: {id}, Type: {islem_tur}, "
                    f"Amount: {tutar}, Account: {hesap_id})"
                )
                return True
            
            except (IntegrityError, SQLAlchemyError) as e:
                session.rollback()
                self.logger.error(f"Atomic transaction failed during delete: {str(e)}")
                raise DatabaseError(
                    f"İşlem silme ve bakiye düzeltmesi başarısız (atomic transaction): {str(e)}",
                    code="DB_DEL_001",
                    details={
                        "islem_id": id,
                        "islem_turu": islem_tur,
                        "hesap_id": hesap_id
                    }
                )
        
        except (NotFoundError, DatabaseError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during delete: {str(e)}")
            raise DatabaseError(
                f"Beklenmeyen hata: {str(e)}",
                code="DB_001",
                details={"error_type": type(e).__name__}
            )
        finally:
            if close_db:
                session.close()
