"""
Temel controller sınıfı - Base CRUD operasyonları.

Bu modül, tüm entity controller'lar tarafından kalıtılan temel controller sınıfını içerir.
Error handling ve veri doğrulama ile geliştirilmiş CRUD operasyonları sağlar.

Classes:
    BaseController: Generic CRUD controller
"""

from typing import List, Optional, TypeVar, Generic, Type, cast
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.config import get_db, get_db_session
from models.base import Base
from models.exceptions import DatabaseError, NotFoundError

# Logger import
from utils.logger import get_logger

T = TypeVar('T', bound=Base)

class BaseController(Generic[T]):
    """
    Temel CRUD işlemleri için controller.
    
    Tüm entity controller'lar (Sakin, Daire, vb.) bu sınıftan türetilir.
    CRUD operasyonları için standardize edilmiş metodlar sağlar.
    
    Attributes:
        model_class (type): İşlem yapılacak model sınıfı
    
    Example:
        >>> from models.base import Sakin
        >>> controller = BaseController(Sakin)
        >>> sakinler = controller.get_all()
    """

    def __init__(self, model_class: Type[T]) -> None:
        """
        Controller'ı başlat.
        
        Args:
            model_class (type): Model sınıfı (örn. Sakin, Daire)
        """
        self.model_class = model_class
        # Logger instance
        self.logger = get_logger(f"{self.__class__.__name__}")

    def get_all(self, db: Optional[Session] = None) -> List[T]:
        """
        Tüm kayıtları getir.
        
        Args:
            db (Session, optional): Veritabanı session. None ise yeni oluşturulur.
        
        Returns:
            List[T]: Tüm kayıtların listesi
        
        Raises:
            DatabaseError: Sorgu çalıştırılamadı ise
        
        Example:
            >>> sakinler = controller.get_all()
        """
        self.logger.debug(f"Fetching all records for model {self.model_class.__name__}")
        if db is None:
            with get_db_session() as session:
                try:
                    query: Query[T] = session.query(self.model_class)
                    records = query.all()
                    self.logger.info(f"Successfully fetched {len(records)} records for model {self.model_class.__name__}")
                    return cast(List[T], records)
                except SQLAlchemyError as e:
                    self.logger.error(f"Failed to fetch records for model {self.model_class.__name__}: {str(e)}")
                    raise DatabaseError(
                        "Kayıtlar sorgulanırken hata oluştu",
                        code="DB_001",
                        details={"model": self.model_class.__name__}
                    )
        else:
            session = db
        try:
            query: Query[T] = session.query(self.model_class)
            records = query.all()
            self.logger.info(f"Successfully fetched {len(records)} records for model {self.model_class.__name__}")
            return cast(List[T], records)
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to fetch records for model {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(
                "Kayıtlar sorgulanırken hata oluştu",
                code="DB_001",
                details={"model": self.model_class.__name__}
            )

    def get_by_id(self, id: int, db: Optional[Session] = None) -> Optional[T]:
        """
        ID'ye göre kayıt getir.
        
        Args:
            id (int): Kayıt ID'si
            db (Session, optional): Veritabanı session
        
        Returns:
            T | None: Bulunan kayıt veya None
        
        Raises:
            DatabaseError: Sorgu çalıştırılamadı ise
        
        Example:
            >>> sakin = controller.get_by_id(5)
        """
        self.logger.debug(f"Fetching record with id {id} for model {self.model_class.__name__}")
        if db is None:
            with get_db_session() as session:
                try:
                    query: Query[T] = session.query(self.model_class)
                    record = query.filter(
                        self.model_class.id == id
                    ).first()

                    if record:
                        self.logger.info(f"Record with id {id} found for model {self.model_class.__name__}")
                    else:
                        self.logger.warning(f"Record with id {id} not found for model {self.model_class.__name__}")
                    return cast(Optional[T], record)
                except SQLAlchemyError as e:
                    self.logger.error(f"Failed to fetch record with id {id} for model {self.model_class.__name__}: {str(e)}")
                    raise DatabaseError(
                        "Kayıt getirilemedi",
                        code="DB_001",
                        details={"model": self.model_class.__name__, "id": id}
                    )
        else:
            session = db

        try:
            query: Query[T] = session.query(self.model_class)
            record = query.filter(
                self.model_class.id == id
            ).first()
            
            if record:
                self.logger.info(f"Record with id {id} found for model {self.model_class.__name__}")
            else:
                self.logger.warning(f"Record with id {id} not found for model {self.model_class.__name__}")
                
            return cast(Optional[T], record)
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to fetch record with id {id} for model {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(
                "Kayıt getirilemedi",
                code="DB_001",
                details={"model": self.model_class.__name__, "id": id}
            )

    def create(self, data: dict, db: Optional[Session] = None) -> T:
        """
        Yeni kayıt oluştur.
        
        Args:
            data (dict): Kayıt verileri
            db (Session, optional): Veritabanı session
        
        Returns:
            T: Oluşturulan kayıt
        
        Raises:
            DatabaseError: Kayıt oluşturulamadı ise
            ValidationError: Veri geçersiz ise (alt sınıflarında)
        
        Example:
            >>> data = {"ad_soyad": "Ali Yıldız", "tc_id": "12345678901"}
            >>> sakin = controller.create(data)
        """
        self.logger.debug(f"Creating new record for model {self.model_class.__name__} with data: {data}")
        if db is None:
            with get_db_session() as session:
                try:
                    obj = self.model_class(**data)
                    session.add(obj)
                    session.commit()
                    session.refresh(obj)
                    self.logger.info(f"Successfully created record with id {obj.id} for model {self.model_class.__name__}")
                    return cast(T, obj)
                except IntegrityError as e:
                    session.rollback()
                    self.logger.error(f"Integrity error while creating record for model {self.model_class.__name__}: {str(e)}")
                    raise DatabaseError(
                        "Benzersiz kayıt ihlali veya veri tipi hatası",
                        code="DB_003",
                        details={"model": self.model_class.__name__}
                    )
                except (TypeError, ValueError) as e:
                    session.rollback()
                    self.logger.error(f"Data type error while creating record for model {self.model_class.__name__}: {str(e)}")
                    raise DatabaseError(
                        f"Veri tipi hatası: {str(e)}",
                        code="DB_005",
                        details={"model": self.model_class.__name__}
                    )
                except SQLAlchemyError as e:
                    session.rollback()
                    self.logger.error(f"Database error while creating record for model {self.model_class.__name__}: {str(e)}")
                    raise DatabaseError(
                        "Kayıt oluşturulurken veritabanı hatası",
                        code="DB_001",
                        details={"model": self.model_class.__name__}
                    )
        else:
            session = db

        try:
            obj = self.model_class(**data)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            self.logger.info(f"Successfully created record with id {obj.id} for model {self.model_class.__name__}")
            return cast(T, obj)
        except IntegrityError as e:
            session.rollback()
            self.logger.error(f"Integrity error while creating record for model {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(
                "Benzersiz kayıt ihlali veya veri tipi hatası",
                code="DB_003",
                details={"model": self.model_class.__name__}
            )
        except (TypeError, ValueError) as e:
            session.rollback()
            self.logger.error(f"Data type error while creating record for model {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(
                f"Veri tipi hatası: {str(e)}",
                code="DB_005",
                details={"model": self.model_class.__name__}
            )
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Database error while creating record for model {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(
                "Kayıt oluşturulurken veritabanı hatası",
                code="DB_001",
                details={"model": self.model_class.__name__}
            )

    def update(self, id: int, data: dict, db: Optional[Session] = None) -> Optional[T]:
        """
        Kayıt güncelle.
        
        Args:
            id (int): Güncellenecek kayıt ID'si
            data (dict): Yeni veriler
            db (Session, optional): Veritabanı session
        
        Returns:
            T | None: Güncellenen kayıt veya None (kayıt yoksa)
        
        Raises:
            DatabaseError: Güncelleme başarısız ise
        
        Example:
            >>> data = {"telefon": "+90 555 123 4567"}
            >>> sakin = controller.update(5, data)
        """
        self.logger.debug(f"Updating record with id {id} for model {self.model_class.__name__} with data: {data}")
        if db is None:
            with get_db_session() as session:
                try:
                    obj = self.get_by_id(id, session)
                    if not obj:
                        self.logger.warning(f"Record with id {id} not found for model {self.model_class.__name__} during update")
                        raise NotFoundError(
                            "Güncellenecek kayıt bulunamadı",
                            code="NOT_FOUND_001",
                            details={"model": self.model_class.__name__, "id": id}
                        )
                    for key, value in data.items():
                        if hasattr(obj, key):
                            setattr(obj, key, value)
                    session.commit()
                    session.refresh(obj)
                    self.logger.info(f"Successfully updated record with id {id} for model {self.model_class.__name__}")
                    return cast(Optional[T], obj)
                except IntegrityError as e:
                    session.rollback()
                    self.logger.error(f"Integrity error while updating record with id {id} for model {self.model_class.__name__}: {str(e)}")
                    raise DatabaseError(
                        "Benzersiz kayıt ihlali veya veri tipi hatası",
                        code="DB_003",
                        details={"model": self.model_class.__name__, "id": id}
                    )
                except (TypeError, ValueError) as e:
                    session.rollback()
                    self.logger.error(f"Data type error while updating record with id {id} for model {self.model_class.__name__}: {str(e)}")
                    raise DatabaseError(
                        f"Veri tipi hatası: {str(e)}",
                        code="DB_005",
                        details={"model": self.model_class.__name__}
                    )
                except SQLAlchemyError as e:
                    session.rollback()
                    self.logger.error(f"Database error while updating record with id {id} for model {self.model_class.__name__}: {str(e)}")
                    raise DatabaseError(
                        "Kayıt güncellenirken veritabanı hatası",
                        code="DB_001",
                        details={"model": self.model_class.__name__, "id": id}
                    )
        else:
            session = db

        try:
            obj = self.get_by_id(id, session)
            
            if not obj:
                self.logger.warning(f"Record with id {id} not found for model {self.model_class.__name__} during update")
                raise NotFoundError(
                    "Güncellenecek kayıt bulunamadı",
                    code="NOT_FOUND_001",
                    details={"model": self.model_class.__name__, "id": id}
                )
            
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            
            session.commit()
            session.refresh(obj)
            self.logger.info(f"Successfully updated record with id {id} for model {self.model_class.__name__}")
            return cast(Optional[T], obj)
        except IntegrityError as e:
            session.rollback()
            self.logger.error(f"Integrity error while updating record with id {id} for model {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(
                "Benzersiz kayıt ihlali veya veri tipi hatası",
                code="DB_003",
                details={"model": self.model_class.__name__, "id": id}
            )
        except (TypeError, ValueError) as e:
            session.rollback()
            self.logger.error(f"Data type error while updating record with id {id} for model {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(
                f"Veri tipi hatası: {str(e)}",
                code="DB_005",
                details={"model": self.model_class.__name__}
            )
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Database error while updating record with id {id} for model {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(
                "Kayıt güncellenirken veritabanı hatası",
                code="DB_001",
                details={"model": self.model_class.__name__, "id": id}
            )
        

    def delete(self, id: int, db: Optional[Session] = None) -> bool:
        """
        Kayıt sil.
        
        Args:
            id (int): Silinecek kayıt ID'si
            db (Session, optional): Veritabanı session
        
        Returns:
            bool: True (başarılı), False (kayıt yoksa)
        
        Raises:
            DatabaseError: Silme başarısız ise
        
        Example:
            >>> success = controller.delete(5)
        """
        self.logger.debug(f"Deleting record with id {id} for model {self.model_class.__name__}")
        if db is None:
            with get_db_session() as session:
                try:
                    obj = self.get_by_id(id, session)
                    if not obj:
                        self.logger.warning(f"Record with id {id} not found for model {self.model_class.__name__} during delete")
                        return False
                    session.delete(obj)
                    session.commit()
                    self.logger.info(f"Successfully deleted record with id {id} for model {self.model_class.__name__}")
                    return True
                except IntegrityError as e:
                    session.rollback()
                    self.logger.error(f"Integrity error while deleting record with id {id} for model {self.model_class.__name__}: {str(e)}")
                    raise DatabaseError(
                        "Referans bütünlüğü ihlali - Bu kaydı silen başka kayıtlar var",
                        code="DB_003",
                        details={"model": self.model_class.__name__, "id": id}
                    )
                except SQLAlchemyError as e:
                    session.rollback()
                    self.logger.error(f"Database error while deleting record with id {id} for model {self.model_class.__name__}: {str(e)}")
                    raise DatabaseError(
                        "Kayıt silinirken veritabanı hatası",
                        code="DB_001",
                        details={"model": self.model_class.__name__, "id": id}
                    )
        else:
            session = db

        try:
            obj = self.get_by_id(id, session)
            
            if not obj:
                self.logger.warning(f"Record with id {id} not found for model {self.model_class.__name__} during delete")
                return False
            
            session.delete(obj)
            session.commit()
            self.logger.info(f"Successfully deleted record with id {id} for model {self.model_class.__name__}")
            return True
        except IntegrityError as e:
            session.rollback()
            self.logger.error(f"Integrity error while deleting record with id {id} for model {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(
                "Referans bütünlüğü ihlali - Bu kaydı silen başka kayıtlar var",
                code="DB_003",
                details={"model": self.model_class.__name__, "id": id}
            )
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Database error while deleting record with id {id} for model {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(
                "Kayıt silinirken veritabanı hatası",
                code="DB_001",
                details={"model": self.model_class.__name__, "id": id}
            )
