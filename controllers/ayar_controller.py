"""
Ayar controller
"""

from typing import Optional, Dict, Any, cast
from sqlalchemy.orm import Session
from controllers.base_controller import BaseController
from models.base import Ayar
from database.config import get_db

# Logger import
from utils.logger import get_logger

class AyarController(BaseController[Ayar]):
    """Ayarlar için controller"""

    def __init__(self) -> None:
        super().__init__(Ayar)
        self.logger = get_logger(f"{self.__class__.__name__}")

    def get_ayar(self, anahtar: str, db: Optional[Session] = None) -> Optional[Ayar]:
        """Belirli bir ayarı getir"""
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            result = db.query(Ayar).filter(Ayar.anahtar == anahtar).first()
            return cast(Optional[Ayar], result)
        finally:
            if close_db and db is not None:
                db.close()

    def set_ayar(self, anahtar: str, deger: str, aciklama: str = "", db: Optional[Session] = None) -> bool:
        """Ayarı oluştur veya güncelle"""
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            # Type ignore to satisfy linter - get_db() always returns a Session
            ayar = self.get_ayar(anahtar, db)
            
            if ayar:
                # Güncelle
                ayar.deger = deger
                ayar.aciklama = aciklama
            else:
                # Yeni oluştur
                ayar = Ayar()
                ayar.anahtar = anahtar
                ayar.deger = deger
                ayar.aciklama = aciklama
                db.add(ayar)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Ayar kaydedilirken hata oluştu: {e}")
            return False
        finally:
            if close_db and db is not None:
                db.close()

    def get_all_ayarlar(self, db: Optional[Session] = None) -> Dict[str, str]:
        """Tüm ayarları sözlük olarak getir"""
        close_db = False
        if db is None:
            db = get_db()
            close_db = True

        try:
            ayarlar = db.query(Ayar).all()
            return {ayar.anahtar: ayar.deger for ayar in ayarlar}
        finally:
            if close_db and db is not None:
                db.close()

    def get_ayar_with_default(self, anahtar: str, default: str = "", db: Optional[Session] = None) -> str:
        """Ayarı getir, yoksa varsayılan değeri döndür"""
        ayar = self.get_ayar(anahtar, db)
        return ayar.deger if ayar else default