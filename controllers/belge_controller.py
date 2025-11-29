"""
Belge yönetimi controller
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Logger import
from utils.logger import get_logger

class BelgeController:
    """Belge yönetimi için controller"""
    
    # Belge klasörü
    BELGELER_KLASORU = "belgeler"
    
    # İzin verilen dosya türleri
    IZIN_VERILEN_TURLER = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.txt': 'text/plain',
        '.zip': 'application/zip'
    }
    
    # Maksimum dosya boyutu (50 MB)
    MAX_DOSYA_BOYUTU = 50 * 1024 * 1024
    
    def __init__(self) -> None:
        """Controller'ı başlat"""
        self._belgeler_klasoru_kontrol_et()
        # Logger instance
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    def _belgeler_klasoru_kontrol_et(self) -> None:
        """Belgeler klasörünü kontrol et ve oluştur"""
        if not os.path.exists(self.BELGELER_KLASORU):
            os.makedirs(self.BELGELER_KLASORU)
    
    def dosya_ekle(self, kaynak_yolu: str, islem_id: int, tur: str) -> Tuple[bool, str, Optional[str]]:
        """
        Dosyayı belgeler klasörüne kopyala ve yolunu döndür
        
        Args:
            kaynak_yolu: Orijinal dosya yolu
            islem_id: İşlem ID'si
            tur: İşlem türü (Gelir, Gider, Transfer)
        
        Returns:
            (başarılı, mesaj, dosya_yolu)
        """
        self.logger.debug(f"Attempting to add file from {kaynak_yolu} for transaction {islem_id}")
        try:
            # Dosya var mı kontrol et
            if not os.path.exists(kaynak_yolu):
                self.logger.warning(f"File not found: {kaynak_yolu}")
                return False, "Dosya bulunamadı!", None
            
            # Dosya boyutunu kontrol et
            dosya_boyutu = os.path.getsize(kaynak_yolu)
            if dosya_boyutu > self.MAX_DOSYA_BOYUTU:
                self.logger.warning(f"File too large: {dosya_boyutu} bytes > {self.MAX_DOSYA_BOYUTU} bytes")
                return False, f"Dosya çok büyük! Maksimum {self.MAX_DOSYA_BOYUTU / (1024*1024):.0f} MB olmalı.", None
            
            # Dosya türünü kontrol et
            _, dosya_uzantisi = os.path.splitext(kaynak_yolu)
            if dosya_uzantisi.lower() not in self.IZIN_VERILEN_TURLER:
                self.logger.warning(f"Unsupported file type: {dosya_uzantisi}")
                uzantı_listesi = ", ".join(self.IZIN_VERILEN_TURLER.keys())
                return False, f"Bu dosya türüne izin yok! İzin verilen: {uzantı_listesi}", None
            
            # Hedef klasörü oluştur
            tur_klasoru = os.path.join(self.BELGELER_KLASORU, tur)
            if not os.path.exists(tur_klasoru):
                os.makedirs(tur_klasoru)
                self.logger.debug(f"Created directory: {tur_klasoru}")
            
            # Yeni dosya adını oluştur (islem_id + timestamp + orijinal uzantı)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            yeni_dosya_adi = f"{islem_id}_{timestamp}{dosya_uzantisi}"
            hedef_yolu = os.path.join(tur_klasoru, yeni_dosya_adi)
            
            # Dosyayı kopyala
            shutil.copy2(kaynak_yolu, hedef_yolu)
            self.logger.debug(f"File copied to: {hedef_yolu}")
            
            # Veritabanında saklanan yolu döndür (relatif yol)
            saklanan_yol = os.path.normpath(os.path.join(tur_klasoru, yeni_dosya_adi)).replace("\\", "/")
            
            self.logger.info(f"File successfully added: {saklanan_yol} (ID: {islem_id})")
            return True, "Belge başarıyla yüklendi!", saklanan_yol
            
        except Exception as e:
            self.logger.error(f"Failed to add file: {str(e)}")
            return False, f"Belge yükleme hatası: {str(e)}", None
    
    def dosya_sil(self, dosya_yolu: str) -> Tuple[bool, str]:
        """
        Belge dosyasını sil
        
        Args:
            dosya_yolu: Silinecek dosya yolu
        
        Returns:
            (başarılı, mesaj)
        """
        self.logger.debug(f"Attempting to delete file: {dosya_yolu}")
        try:
            if not dosya_yolu:
                self.logger.warning("File path not specified for deletion")
                return False, "Dosya yolu belirtilmedi!"
            
            # Tam yol oluştur
            tam_yol = os.path.abspath(dosya_yolu)
            
            if os.path.exists(tam_yol):
                os.remove(tam_yol)
                self.logger.info(f"File successfully deleted: {tam_yol}")
                return True, "Belge başarıyla silindi!"
            else:
                self.logger.warning(f"File not found for deletion: {tam_yol}")
                return False, f"Dosya bulunamadı! ({tam_yol})"
        except Exception as e:
            self.logger.error(f"Failed to delete file: {str(e)}")
            return False, f"Belge silme hatası: {str(e)}"
    
    def dosya_var_mi(self, dosya_yolu: str) -> bool:
        """Dosyanın var olup olmadığını kontrol et"""
        if not dosya_yolu:
            return False
        return os.path.exists(dosya_yolu)
    
    def dosya_ac(self, dosya_yolu: str) -> Tuple[bool, str]:
        """Belge dosyasını aç (sistem varsayılan programıyla)"""
        self.logger.debug(f"Attempting to open file: {dosya_yolu}")
        try:
            if not dosya_yolu:
                self.logger.warning("File path not specified for opening")
                return False, "Dosya yolu belirtilmedi!"
            
            # Tam yol oluştur
            tam_yol = os.path.abspath(dosya_yolu)
            
            if not os.path.exists(tam_yol):
                self.logger.warning(f"File not found for opening: {tam_yol}")
                return False, f"Dosya bulunamadı! ({tam_yol})"
            
            # Windows
            if os.name == 'nt':
                os.startfile(tam_yol)
            # Mac
            elif os.name == 'posix' and 'darwin' in sys.platform:
                os.system(f'open "{tam_yol}"')
            # Linux
            else:
                os.system(f'xdg-open "{tam_yol}"')
            
            self.logger.info(f"File opened: {tam_yol}")
            return True, "Dosya açılıyor..."
        except Exception as e:
            self.logger.error(f"Failed to open file: {str(e)}")
            return False, f"Dosya açma hatası: {str(e)}"
    
    def dosya_adi_al(self, dosya_yolu: str) -> str:
        """Dosya yolundan sadece dosya adını al"""
        if not dosya_yolu:
            return ""
        return os.path.basename(dosya_yolu)
