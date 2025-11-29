"""
Yedekleme ve geri yükleme işlemleri controller
"""

import os
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, List, Dict, Any, Type
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from database.config import get_db, engine, Base
from models.base import (
    Lojman, Blok, Daire, Sakin, Aidat, AidatIslem, AidatOdeme,
    Hesap, Kategori, FinansIslem, Ayar, AnaKategori, AltKategori, Finans
)

# Logger import
from utils.logger import get_logger

class BackupController:
    """Yedekleme ve geri yükleme işlemleri"""

    # Model sırası (foreign key dependencies için önemli)
    MODELS_ORDER: List[Type[Base]] = [
        Lojman, Blok, Daire, Sakin, Aidat, AidatIslem, AidatOdeme,
        Hesap, Kategori, FinansIslem, Ayar, AnaKategori, AltKategori, Finans
    ]

    def __init__(self) -> None:
        """
        BackupController'ı başlat.
        
        Database session'ını None ile başlatır ve logger instance'ı oluşturur.
        """
        self.db = None
        # Logger instance
        self.logger = get_logger(f"{self.__class__.__name__}")

    def get_database_info(self) -> Dict[str, int]:
        """Veritabanı bilgilerini al (tablo başına satır sayısı)"""
        try:
            db = self._get_db()
            info = {}
            
            for model in self.MODELS_ORDER:
                count = db.query(model).count()
                if count > 0:
                    table_name = model.__tablename__
                    info[table_name] = count
            
            return info
        except Exception as e:
            print(f"Veritabanı bilgisi alınamadı: {str(e)}")
            return {}
        finally:
            self._close_db()
    
    def reset_database(self) -> bool:
        """
        Veritabanını sıfırla - tüm verileri sil
        
        Returns:
            bool: Başarılı olup olmadığı
        """
        try:
            db = self._get_db()
            
            # Tüm verileri ters sırada sil (foreign key constraints)
            for model in reversed(self.MODELS_ORDER):
                db.query(model).delete()
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Veritabanı sıfırlama hatası: {str(e)}")
            return False
        finally:
            self._close_db()

    def _get_db(self) -> Session:
        """
        Veritabanı session'ı al veya oluştur.
        
        Returns:
            Session: SQLAlchemy database session
        """
        if self.db is None:
            self.db = get_db()
        return self.db

    def _close_db(self) -> None:
        """
        Veritabanı session'ını kapat.
        
        Session varsa kapatır ve None'a ayarlar.
        """
        if self.db:
            self.db.close()
            self.db = None

    def backup_to_excel(self, filepath: str) -> bool:
        """
        Veritabanını Excel formatında yedekle
        
        Args:
            filepath: Kaydedilecek dosya yolu
            
        Returns:
            bool: Başarılı olup olmadığı
        """
        try:
            db = self._get_db()
            
            # Excel yazıcısını oluştur
            excel_file = pd.ExcelWriter(filepath, engine='openpyxl')
            
            # Her tablo için verileri Excel'e yaz
            for model in self.MODELS_ORDER:
                table_name = model.__tablename__
                
                # Verileri sor
                data = db.query(model).all()
                
                if data:
                    # Modeli DataFrame'e çevir
                    df = self._model_list_to_dataframe(data)
                    
                    # Excel'e yaz
                    df.to_excel(excel_file, sheet_name=table_name, index=False)
            
            excel_file.close()
            return True
            
        except Exception as e:
            print(f"Excel yedekleme hatası: {str(e)}")
            return False
        finally:
            self._close_db()

    def backup_to_xml(self, filepath: str) -> bool:
        """
        Veritabanını XML formatında yedekle
        
        Args:
            filepath: Kaydedilecek dosya yolu
            
        Returns:
            bool: Başarılı olup olmadığı
        """
        try:
            db = self._get_db()
            
            # Root element oluştur
            root = ET.Element("YedekVeri")
            root.set("tarih", datetime.now().isoformat())
            root.set("versiyon", "1.0")
            
            # Her tablo için veri ekle
            for model in self.MODELS_ORDER:
                table_name = model.__tablename__
                
                # Verileri sor
                data = db.query(model).all()
                
                if data:
                    # Tablo elementi oluştur
                    table_element = ET.SubElement(root, "Tablo")
                    table_element.set("ad", table_name)
                    
                    # Her satırı XML'e ekle
                    for row in data:
                        row_element = ET.SubElement(table_element, "Satir")
                        
                        # Kolon değerlerini ekle
                        mapper = inspect(model)
                        for column in mapper.columns:
                            col_name = column.name
                            col_value = getattr(row, col_name, None)
                            
                            # Değeri string'e çevir
                            if col_value is not None:
                                if isinstance(col_value, datetime):
                                    col_value = col_value.isoformat()
                                else:
                                    col_value = str(col_value)
                            
                            # Element ekle
                            col_element = ET.SubElement(row_element, col_name)
                            col_element.text = col_value or ""
            
            # XML'i dosyaya yaz
            tree = ET.ElementTree(root)
            ET.indent(root, space="  ")  # Formatla
            tree.write(filepath, encoding='utf-8', xml_declaration=True)
            
            return True
            
        except Exception as e:
            print(f"XML yedekleme hatası: {str(e)}")
            return False
        finally:
            self._close_db()

    def restore_from_excel(self, filepath: str) -> bool:
        """
        Excel dosyasından veritabanını geri yükle
        
        Args:
            filepath: Yüklenecek dosya yolu
            
        Returns:
            bool: Başarılı olup olmadığı
        """
        try:
            db = self._get_db()
            
            # Excel dosyasını oku
            try:
                xls = pd.ExcelFile(filepath)
            except Exception as e:
                print(f"Excel dosyası okunurken hata: {str(e)}")
                return False
            
            # Önce veritabanını temizle
            try:
                self._clear_database(db)
            except Exception as e:
                print(f"Veritabanı temizleme başarısız: {str(e)}")
                db.rollback()
                return False
            
            # Sheet sırasına göre (foreign key dependencies)
            for model in self.MODELS_ORDER:
                table_name = model.__tablename__
                
                # Sheet varsa oku
                if table_name in xls.sheet_names:
                    try:
                        df = pd.read_excel(filepath, sheet_name=table_name)
                        row_count = 0
                        
                        # Her satırı database'e ekle
                        for _, row in df.iterrows():
                            # NaN değerleri None'a çevir
                            row_dict = row.where(pd.notna(row), None).to_dict()
                            
                            # Model instance'ı oluştur
                            try:
                                instance = model(**row_dict)
                                db.add(instance)
                                row_count += 1
                            except Exception as e:
                                print(f"Satır eklerken hata ({table_name}): {str(e)}")
                                db.rollback()
                                return False
                        
                        # Commit et
                        db.commit()
                        print(f"{table_name}: {row_count} satır yüklendi")
                        
                    except Exception as e:
                        print(f"Excel sheet okunurken hata ({table_name}): {str(e)}")
                        db.rollback()
                        return False
            
            print("Excel geri yükleme başarılı")
            return True
            
        except Exception as e:
            print(f"Excel geri yükleme genel hatası: {str(e)}")
            import traceback
            traceback.print_exc()
            if db:
                db.rollback()
            return False
        finally:
            self._close_db()

    def restore_from_xml(self, filepath: str) -> bool:
        """
        XML dosyasından veritabanını geri yükle
        
        Args:
            filepath: Yüklenecek dosya yolu
            
        Returns:
            bool: Başarılı olup olmadığı
        """
        try:
            db = self._get_db()
            
            # XML'i oku
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
            except ET.ParseError as pe:
                print(f"XML dosyası okunurken hata: {str(pe)}")
                db.rollback()
                return False
            
            # Önce veritabanını temizle
            try:
                self._clear_database(db)
            except Exception as e:
                print(f"Veritabanı temizleme başarısız: {str(e)}")
                db.rollback()
                return False
            
            # Her tablo için veri ekle
            for table_elem in root.findall("Tablo"):
                table_name = table_elem.get("ad")
                
                # Modeli bul
                if table_name is not None:
                    model = self._get_model_by_table_name(table_name)
                    if not model:
                        print(f"Model bulunamadı: {table_name}")
                        continue
                else:
                    print("Geçersiz tablo adı")
                    continue
                
                # Her satırı işle
                row_count = 0
                for row_elem in table_elem.findall("Satir"):
                    row_dict = {}
                    
                    # Kolon değerlerini oku
                    for col_elem in row_elem:
                        col_name = col_elem.tag
                        col_value = col_elem.text or None
                        
                        # Tip dönüştürmesi yap
                        col_value = self._convert_value(model, col_name, col_value)
                        
                        row_dict[col_name] = col_value
                    
                    # Model instance'ı oluştur ve ekle
                    if row_dict:
                        try:
                            instance = model(**row_dict)
                            db.add(instance)
                            row_count += 1
                        except TypeError as te:
                            # Bilinmeyen kolon varsa atla
                            print(f"Satır eklerken TypeError ({table_name}): {str(te)}")
                            continue
                        except Exception as e:
                            print(f"Satır eklerken hata ({table_name}): {str(e)}")
                            db.rollback()
                            return False
                
                # Commit et
                try:
                    db.commit()
                    print(f"{table_name}: {row_count} satır yüklendi")
                except Exception as e:
                    print(f"Commit hatası ({table_name}): {str(e)}")
                    db.rollback()
                    return False
            
            print("XML geri yükleme başarılı")
            return True
            
        except Exception as e:
            print(f"XML geri yükleme genel hatası: {str(e)}")
            import traceback
            traceback.print_exc()
            if db:
                db.rollback()
            return False
        finally:
            self._close_db()

    def _clear_database(self, db: Session) -> None:
        """
        Veritabanını temizle - tüm tabloları boşalt.
        
        Foreign key constraints'lerini göz önünde tutarak ters sırada siler.
        
        Args:
            db: SQLAlchemy database session
            
        Raises:
            Exception: Temizleme işlemi başarısız olursa
        """
        try:
            # Ters sırada temizle (foreign key constraints)
            for model in reversed(self.MODELS_ORDER):
                db.query(model).delete()
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Veritabanı temizleme hatası: {str(e)}")
            raise

    def _model_list_to_dataframe(self, data: List[Any]) -> pd.DataFrame:
        """
        Model instance listesini Pandas DataFrame'e çevir.
        
        Args:
            data: ORM model instance'larının listesi
            
        Returns:
            pd.DataFrame: Model verilerinin DataFrame temsili
        """
        if not data:
            return pd.DataFrame()
        
        # İlk instance'dan kolon adlarını al
        first_obj = data[0]
        mapper = inspect(first_obj.__class__)
        
        rows = []
        for obj in data:
            row = {}
            for column in mapper.columns:
                col_name = column.name
                col_value = getattr(obj, col_name, None)
                row[col_name] = col_value
            rows.append(row)
        
        return pd.DataFrame(rows)

    def _get_model_by_table_name(self, table_name: str) -> Optional[type]:
        """
        Tablo adından model sınıfını bul.
        
        Args:
            table_name: Aranacak tablo adı
            
        Returns:
            type | None: Model sınıfı veya bulunamazsa None
        """
        for model in self.MODELS_ORDER:
            if model.__tablename__ == table_name:
                return model
        return None

    def _convert_value(self, model: type, column_name: str, value: Optional[str]) -> Any:
        """
        String değerini model kolon tipi göre uygun tipe çevir.
        
        Args:
            model: ORM model sınıfı
            column_name: Kolon adı
            value: Dönüştürülecek string değeri
            
        Returns:
            Any: Uygun tipte dönüştürülmüş değer
        """
        if value is None or value == 'None':
            return None
        
        if isinstance(value, str):
            value = value.strip()
        
        if not value:
            return None
            
        try:
            mapper = inspect(model)
            
            # Kolon tipini bul
            col_type = None
            for col in mapper.columns:
                if col.name == column_name:
                    col_type = str(col.type)
                    break
            
            if col_type is None:
                return value
            
            # Tip dönüştürmesi
            if "INTEGER" in col_type or "INT" in col_type:
                try:
                    return int(float(value)) if value else None
                except (ValueError, TypeError):
                    return None
            elif "FLOAT" in col_type or "NUMERIC" in col_type:
                try:
                    return float(value) if value else None
                except (ValueError, TypeError):
                    return None
            elif "BOOLEAN" in col_type or "BOOL" in col_type:
                # String boolean değeri Python boolean'a çevir
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif "DATETIME" in col_type or "DATE" in col_type:
                # ISO format tarih string'ini parse et
                if value and value != 'None':
                    try:
                        return datetime.fromisoformat(value)
                    except ValueError:
                        return None
                return None
            else:
                return value
        
        except Exception as e:
            print(f"Değer dönüştürme hatası ({column_name}={value}): {str(e)}")
            return value

    def backup_database_file(self, target_dir: str) -> bool:
        """
        Veritabanı dosyasını doğrudan kopyala
        
        Args:
            target_dir: Hedef dizin
            
        Returns:
            bool: Başarılı olup olmadığı
        """
        try:
            # Farklı olası yollar dene
            db_paths = [
                "./aidat_plus.db",
                "aidat_plus.db",
                os.path.join(os.getcwd(), "aidat_plus.db")
            ]
            
            db_file = None
            for path in db_paths:
                if os.path.exists(path):
                    db_file = path
                    break
            
            if db_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                target_file = os.path.join(target_dir, f"aidat_plus_backup_{timestamp}.db")
                shutil.copy2(db_file, target_file)
                return True
            return False
        except Exception as e:
            print(f"Veritabanı dosyası yedekleme hatası: {str(e)}")
            return False
