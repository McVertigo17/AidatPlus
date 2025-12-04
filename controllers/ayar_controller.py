"""
Ayar controller
"""

from typing import Optional, Dict, Any, cast
from sqlalchemy.orm import Session
from controllers.base_controller import BaseController
from models.base import Ayar
from database.config import get_db, get_db_session

# Logger import
from utils.logger import get_logger

class AyarController(BaseController[Ayar]):
    """Ayarlar için controller"""

    def __init__(self) -> None:
        super().__init__(Ayar)
        self.logger = get_logger(f"{self.__class__.__name__}")

    def get_ayar(self, anahtar: str, db: Optional[Session] = None) -> Optional[Ayar]:
        """Belirli bir ayarı getir"""
        if db is None:
            with get_db_session() as session:
                result = session.query(Ayar).filter(Ayar.anahtar == anahtar).first()
                return cast(Optional[Ayar], result)
        else:
            result = db.query(Ayar).filter(Ayar.anahtar == anahtar).first()
            return cast(Optional[Ayar], result)

    def set_ayar(self, anahtar: str, deger: str, aciklama: str = "", db: Optional[Session] = None) -> bool:
        """Ayarı oluştur veya güncelle"""
        if db is None:
            with get_db_session() as session:
                try:
                    ayar = self.get_ayar(anahtar, session)
                    if ayar:
                        ayar.deger = deger
                        ayar.aciklama = aciklama
                    else:
                        ayar = Ayar(anahtar=anahtar, deger=deger, aciklama=aciklama)
                        session.add(ayar)
                    session.commit()
                    return True
                except Exception as e:
                    session.rollback()
                    print(f"Ayar kaydedilirken hata oluştu: {e}")
                    return False
        else:
            try:
                ayar = self.get_ayar(anahtar, db)
                if ayar:
                    ayar.deger = deger
                    ayar.aciklama = aciklama
                else:
                    ayar = Ayar(anahtar=anahtar, deger=deger, aciklama=aciklama)
                    db.add(ayar)
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                print(f"Ayar kaydedilirken hata oluştu: {e}")
                return False

    def get_all_ayarlar(self, db: Optional[Session] = None) -> Dict[str, str]:
        """Tüm ayarları sözlük olarak getir"""
        if db is None:
            with get_db_session() as session:
                ayarlar = session.query(Ayar).all()
                return {ayar.anahtar: ayar.deger for ayar in ayarlar}
        else:
            ayarlar = db.query(Ayar).all()
            return {ayar.anahtar: ayar.deger for ayar in ayarlar}

    def get_ayar_with_default(self, anahtar: str, default: str = "", db: Optional[Session] = None) -> str:
        """Ayarı getir, yoksa varsayılan değeri döndür"""
        ayar = self.get_ayar(anahtar, db)
        return ayar.deger if ayar else default