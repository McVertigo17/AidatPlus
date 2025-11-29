# Aidat Plus - Utilities Rehberi

**Son Güncelleme**: 29 Kasım 2025  
**Sürüm**: v1.2  
**Durum**: ✅ Utilities %100 Docstring Coverage

---

## 📚 İçindekiler

1. [Logger Sistemi](#logger-sistemi)
2. [Utility Fonksiyonları](#utility-fonksiyonları)
3. [Best Practices](#best-practices)
4. [Örnekler](#örnekler)

---

## Logger Sistemi

### Genel Bakış

`utils/logger.py` modülü, Aidat Plus uygulaması için merkezi logging çözümü sağlar.

**Özellikler**:
- ✅ File ve console output
- ✅ Rotating file handler (10MB limit, 5 backup)
- ✅ Farklı formatter'lar (file vs. console)
- ✅ 5 log seviyesi: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ Türkçe mesaj desteği
- ✅ Tarih formatında log dosyaları: `aidat_plus_YYYY-MM-DD.log`

---

### AidatPlusLogger Sınıfı

#### İnstansiyasyon

```python
from utils.logger import AidatPlusLogger, get_logger, logger

# Yöntem 1: get_logger() fonksiyonu (önerilen)
logger = get_logger("ModuleeName")

# Yöntem 2: Direkt sınıf oluşturma
custom_logger = AidatPlusLogger("MyLogger", log_level=logging.DEBUG)

# Yöntem 3: Global logger
from utils.logger import logger
logger.info("Uygulamaya hoş geldiniz")
```

#### Constructor

```python
def __init__(self, name: str = "AidatPlus", log_level: int = logging.INFO):
    """
    Initialize the logger with file and console handlers.
    
    Args:
        name: Logger name (typically module name)
        log_level: Minimum level to log
    """
```

**Parametreler**:
- `name` (str): Logger adı. Önerilen format: `"ModuleName"` (ör. `"SakinController"`)
- `log_level` (int): Minimum log seviyesi
  - `logging.DEBUG` (10) - En detaylı
  - `logging.INFO` (20) - Bilgilendirme
  - `logging.WARNING` (30) - Uyarılar
  - `logging.ERROR` (40) - Hatalar
  - `logging.CRITICAL` (50) - Kritik sorunlar

#### Log Metodları

**1. debug(message: str)**
```python
logger.debug("Detaylı geliştirme bilgisi")
# Çıktı: DEBUG - AidatPlus - Detaylı geliştirme bilgisi
```

**2. info(message: str)**
```python
logger.info("Sakin başarıyla oluşturuldu: Ali Yıldız")
# Çıktı: INFO - AidatPlus - Sakin başarıyla oluşturuldu: Ali Yıldız
```

**3. warning(message: str)**
```python
logger.warning("Bakiye negatif değer içeriyor")
# Çıktı: WARNING - AidatPlus - Bakiye negatif değer içeriyor
```

**4. error(message: str)**
```python
logger.error("Veritabanı bağlantı hatası: Connection refused")
# Çıktı: ERROR - AidatPlus - Veritabanı bağlantı hatası: Connection refused
```

**5. critical(message: str)**
```python
logger.critical("Sistem başarısız: Veritabanı tamamen kullanılamıyor")
# Çıktı: CRITICAL - AidatPlus - Sistem başarısız: Veritabanı tamamen kullanılamıyor
```

---

### Log Dosyası Formatı

#### File Handler Formatı
```
2025-11-29 14:35:42,123 - AidatPlus - INFO - sakin_panel.py:45 - load_aktif_sakinler() - 12 aktif sakin yüklendi
```

**Bileşenler**:
- `2025-11-29 14:35:42,123` - Zaman damgası (YYYY-MM-DD HH:MM:SS,milliseconds)
- `AidatPlus` - Logger adı
- `INFO` - Log seviyesi
- `sakin_panel.py:45` - Dosya adı ve satır numarası
- `load_aktif_sakinler()` - Fonksiyon adı
- `12 aktif sakin yüklendi` - Mesaj

#### Console Handler Formatı
```
INFO - AidatPlus - 12 aktif sakin yüklendi
```

**Bileşenler**:
- `INFO` - Log seviyesi
- `AidatPlus` - Logger adı
- `12 aktif sakin yüklendi` - Mesaj

---

### Log Dosyaları

**Depo**: `logs/` klasörü

**Dosya Adlandırması**: `aidat_plus_YYYY-MM-DD.log`

**Örnek**:
```
logs/aidat_plus_2025-11-29.log
logs/aidat_plus_2025-11-28.log
logs/aidat_plus_2025-11-27.log
```

**Rotating Handler Konfigürasyonu**:
- **Max Size**: 10 MB
- **Backup Count**: 5 (eski dosyalar tutulur)
- **Format**: `aidat_plus_{original}.log.1`, `.log.2`, vb.

---

## UTF-8 Encoding Desteği

Logger, Turkish karakterleri ve emoji'leri desteklemek için UTF-8 encoding kullanır:

**Features**:
- ✅ Türkçe karakterler (ü, ö, ş, ç, ğ, ı)
- ✅ Emoji desteği (📊, 🔴, 🟢, 🔵, vb.)
- ✅ Windows/Linux/macOS compatibility
- ✅ File handler: `utf-8` encoding
- ✅ Console handler: UTF-8 reconfigure (Windows uyumlu)

**Örnek**:
```python
logger.info("Dashboard başlatıldı - 📊 Panel")  # Emoji + Türkçe
logger.warning("Bakiye uyarısı: 📉 Düşüş detected")  # Emoji + Türkçe
```

---

## Utility Fonksiyonları

### get_logger(name: str) → AidatPlusLogger

Logger örneğini alır veya oluşturur.

```python
def get_logger(name: str = "AidatPlus") -> AidatPlusLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Configured AidatPlusLogger instance
    """
    return AidatPlusLogger(name)
```

**Örnek Kullanım**:
```python
# Controller'da
from utils.logger import get_logger

class SakinController(BaseController):
    def __init__(self):
        super().__init__(Sakin)
        self.logger = get_logger("SakinController")
    
    def create_sakin(self, ad_soyad: str, tc_id: str, **kwargs):
        self.logger.info(f"Yeni sakin oluşturma başlatıldı: {ad_soyad}")
        try:
            # İşlemler...
            self.logger.info(f"Sakin başarıyla oluşturuldu: {ad_soyad}")
            return sakin
        except Exception as e:
            self.logger.error(f"Sakin oluşturma başarısız: {str(e)}")
            raise
```

### Global Logger Instance

`logger` - Pre-configured global logger

```python
from utils.logger import logger

logger.info("Uygulama başlatılıyor...")
logger.warning("Şu an 50 sakin yüklü")
```

---

## Best Practices

### 1. Logger İnstansiyasyonu

**✅ Doğru**:
```python
# Controller'da
class SakinController(BaseController):
    def __init__(self):
        super().__init__(Sakin)
        self.logger = get_logger("SakinController")
    
    def create_sakin(self, ...):
        self.logger.info("İşlem başladı")
```

**❌ Yanlış**:
```python
# Her metodda logger oluşturma
def create_sakin(self, ...):
    logger = get_logger("SakinController")  # Gereksiz
    logger.info("İşlem başladı")
```

### 2. Log Mesaj Düzeyi Seçimi

| Seviye | Kullanım | Örnek |
|--------|----------|-------|
| **DEBUG** | Geliştirme sırasında detaylı bilgi | `logger.debug("Query: SELECT * FROM...")` |
| **INFO** | Önemli işlem başarısını belgelemek | `logger.info("Sakin başarıyla oluşturuldu")` |
| **WARNING** | Potansiyel sorunlar | `logger.warning("Bakiye negatif olabilir")` |
| **ERROR** | İşlem başarısızlığı | `logger.error("Veritabanı hatası: " + str(e))` |
| **CRITICAL** | Sistem çöküşü riski | `logger.critical("Veritabanı bağlantısı kapandı")` |

### 3. Anlamlı Mesajlar

**✅ Doğru**:
```python
logger.info(f"Sakin {ad_soyad} (TC: {tc_id}) başarıyla oluşturuldu")
logger.error(f"Sakin silme başarısız - ID: {sakin_id}, Hata: {str(e)}")
```

**❌ Yanlış**:
```python
logger.info("Done")
logger.error("Error")
```

### 4. Exception Logging

**✅ Doğru**:
```python
try:
    sakin = self.create_sakin(data)
    self.logger.info("Sakin oluşturuldu")
except ValidationError as e:
    self.logger.error(f"Validasyon hatası: {str(e.message)}")
except DatabaseError as e:
    self.logger.critical(f"Veritabanı hatası: {str(e.message)}")
```

**❌ Yanlış**:
```python
try:
    sakin = self.create_sakin(data)
except Exception as e:
    self.logger.error("Hata oluştu")  # Detay yok
```

### 5. Hassas Bilgileri Maskeleme

**✅ Doğru**:
```python
# TC ID maskeleme
logger.info(f"Sakin kaydedildi - TC: {tc_id[:2]}****{tc_id[-2:]}")
# Telefon maskeleme
logger.info(f"SMS gönderildi - Tel: {telefon[:5]}***{telefon[-3:]}")
```

**❌ Yanlış**:
```python
logger.info(f"Sakin kaydedildi - TC: {tc_id}")  # Hassas veri açıkta
logger.info(f"SMS gönderildi - Tel: {telefon}")
```

### 6. Performans Gözlemleme

```python
import time

def load_sakinler(self):
    start_time = time.time()
    self.logger.debug(f"Sakinler yükleniyor...")
    
    try:
        sakinler = self.session.query(Sakin).all()
        duration = time.time() - start_time
        self.logger.info(f"{len(sakinler)} sakin yüklendi ({duration:.2f}s)")
        return sakinler
    except Exception as e:
        self.logger.error(f"Sakin yükleme başarısız: {str(e)}")
        raise
```

---

## Örnekler

### Örnek 1: Controller'da Logging

```python
# controllers/sakin_controller.py

from utils.logger import get_logger
from models.base import Sakin
from models.exceptions import ValidationError, DatabaseError

class SakinController(BaseController):
    def __init__(self):
        super().__init__(Sakin)
        self.logger = get_logger("SakinController")
    
    def create_sakin(self, ad_soyad: str, tc_id: str, **kwargs) -> Sakin:
        """Yeni sakin oluştur"""
        self.logger.debug(f"create_sakin() çağrıldı - ad_soyad={ad_soyad}")
        
        try:
            # Validasyon
            if not ad_soyad or len(ad_soyad) < 2:
                self.logger.warning(f"Geçersiz ad_soyad: '{ad_soyad}'")
                raise ValidationError("Ad soyad en az 2 karakter olmalı")
            
            # Kayıt oluşturma
            sakin = Sakin(ad_soyad=ad_soyad, tc_id=tc_id, **kwargs)
            self.session.add(sakin)
            self.session.commit()
            
            self.logger.info(f"Sakin başarıyla oluşturuldu: {ad_soyad} (TC: {tc_id[:2]}****)")
            return sakin
            
        except ValidationError as e:
            self.logger.error(f"Validasyon hatası: {str(e.message)}")
            self.session.rollback()
            raise
        except Exception as e:
            self.logger.error(f"Sakin oluşturma başarısız: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Sakin oluşturulamadı: {str(e)}")
    
    def delete_sakin(self, sakin_id: int) -> bool:
        """Sakin sil"""
        self.logger.debug(f"delete_sakin() çağrıldı - sakin_id={sakin_id}")
        
        try:
            sakin = self.session.query(Sakin).filter_by(id=sakin_id).first()
            if not sakin:
                self.logger.warning(f"Sakin bulunamadı - ID: {sakin_id}")
                raise NotFoundError(f"Sakin (ID: {sakin_id}) bulunamadı")
            
            ad_soyad = sakin.ad_soyad
            self.session.delete(sakin)
            self.session.commit()
            
            self.logger.info(f"Sakin silindi: {ad_soyad} (ID: {sakin_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Sakin silme başarısız - ID: {sakin_id}, Hata: {str(e)}")
            self.session.rollback()
            raise
```

### Örnek 2: UI Panel'de Logging

```python
# ui/sakin_panel.py

from utils.logger import get_logger
from models.exceptions import ValidationError, DatabaseError

class SakinPanel(BasePanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = get_logger("SakinPanel")
        self.logger.info("SakinPanel başlatıldı")
    
    def load_aktif_sakinler(self):
        """Aktif sakinleri yükle"""
        self.logger.debug("load_aktif_sakinler() çağrıldı")
        
        try:
            sakinler = self.controller.get_aktif_sakinler()
            self.logger.info(f"{len(sakinler)} aktif sakin yüklendi")
            
            # Treeview'e ekle
            self.tree.delete(*self.tree.get_children())
            for sakin in sakinler:
                self.tree.insert("", tk.END, values=(sakin.id, sakin.ad_soyad, sakin.telefon))
                
        except DatabaseError as e:
            self.logger.error(f"Sakin yükleme başarısız: {str(e.message)}")
            messagebox.showerror("Hata", str(e.message))
        except Exception as e:
            self.logger.critical(f"Beklenmeyen hata: {str(e)}")
            messagebox.showerror("Sistem Hatası", f"Beklenmeyen hata: {str(e)}")
    
    def save_sakin(self):
        """Sakin kaydet"""
        self.logger.debug("save_sakin() çağrıldı")
        
        try:
            ad_soyad = self.entry_ad.get().strip()
            tc_id = self.entry_tc.get().strip()
            
            if not ad_soyad:
                self.logger.warning("Ad-soyad boş bırakıldı")
                raise ValidationError("Ad-soyad boş olamaz")
            
            sakin = self.controller.create_sakin(ad_soyad, tc_id)
            self.logger.info(f"Sakin kaydedildi: {ad_soyad}")
            messagebox.showinfo("Başarılı", "Sakin başarıyla kaydedildi")
            self.load_aktif_sakinler()
            
        except ValidationError as e:
            self.logger.error(f"Validasyon hatası: {str(e.message)}")
            messagebox.showerror("Hata", str(e.message))
```

### Örnek 3: Batch İşlemleri Logging

```python
from utils.logger import get_logger

def import_sakinler_from_excel(file_path: str):
    """Excel'den sakinleri toplu import et"""
    logger = get_logger("ImportSakinler")
    
    logger.info(f"Excel import başladı: {file_path}")
    
    try:
        # Dosyayı oku
        df = pd.read_excel(file_path)
        logger.info(f"Excel dosyası okundu - {len(df)} satır")
        
        controller = SakinController()
        success_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                sakin = controller.create_sakin(
                    ad_soyad=row['Ad Soyad'],
                    tc_id=row['TC ID'],
                    telefon=row.get('Telefon', '')
                )
                success_count += 1
                logger.debug(f"Satır {idx+1} başarılı: {row['Ad Soyad']}")
                
            except ValidationError as e:
                error_count += 1
                logger.warning(f"Satır {idx+1} başarısız: {str(e.message)}")
        
        logger.info(f"Excel import tamamlandı - Başarılı: {success_count}, Başarısız: {error_count}")
        return success_count, error_count
        
    except Exception as e:
        logger.error(f"Excel import başarısız: {str(e)}")
        raise
```

---

## Log Analizi

### Log Dosyasını İnceleme

```bash
# Son 100 satırı gör
tail -n 100 logs/aidat_plus_2025-11-29.log

# Hata satırlarını filtrele
grep "ERROR" logs/aidat_plus_2025-11-29.log

# Belirli bir sakin hakkında
grep "Ali Yıldız" logs/aidat_plus_2025-11-29.log

# Son bir saatte oluşan hataları
grep "ERROR\|CRITICAL" logs/aidat_plus_2025-11-29.log | tail -n 50
```

### Önemli Log Seviyeleri

**Monitoring (Günlük)**:
- `ERROR` ve `CRITICAL` - Acil dikkat gerekli
- `WARNING` - Olası sorunlar

**Geliştirme (Development)**:
- Tüm seviyeler (DEBUG + others)

---

## Sık Sorulan Sorular

**S: Log dosyaları nereye kaydediliyor?**  
C: `logs/aidat_plus_YYYY-MM-DD.log` dosyasına

**S: Eski log dosyaları silinir mi?**  
C: Rotating handler 10MB'ye ulaştığında yeni dosya oluşturur, max 5 backup tutar

**S: Logger'ı her metodda mi oluşturmalıyım?**  
C: Hayır, sınıf içinde bir kez `__init__`'de oluştur

**S: Hassas bilgileri loglayabilir miyim?**  
C: Hayır, TC ID, telefon, email vb. maskelenmelidir

---

**Son Güncelleme**: 29 Kasım 2025  
**Versiyon**: v1.2  
**Utilities Docstring Coverage**: ✅ %100
