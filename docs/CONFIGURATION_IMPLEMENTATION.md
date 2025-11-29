# Configuration Management Implementation

Configuration Management sisteminin projeye uygulanması hakkında rehber.

## ✅ Yapılan Değişiklikler

### 1. Yeni Dosyalar

| Dosya | Amaç |
|-------|------|
| `configuration/config_manager.py` | Merkezi Configuration Manager (900+ satır) |
| `configuration/constants.py` | Configuration keys constants (300+ satır) |
| `configuration/__init__.py` | Package exports |
| `config/app_config.json` | Genel uygulama ayarları |
| `config/user_preferences.json` | Kullanıcı tercihler |
| `.env.example` | Environment variables template |
| `docs/CONFIGURATION_MANAGEMENT.md` | Kapsamlı dokümantasyon |

### 2. Güncellenmiş Dosyalar

#### `main.py`
```python
# 1. Configuration Manager'ı başlat
from configuration import ConfigurationManager, ConfigKeys
config_mgr = ConfigurationManager.get_instance()

# 2. Logging ayarlarını konfigürasyondan al
logging_level = config_mgr.get(ConfigKeys.LOGGING_LEVEL, 'INFO')

# 3. Konfigürasyon ile UI başlat
theme = self.config.get(ConfigKeys.UI_THEME, 'dark')
window_width = self.config.get(ConfigKeys.UI_DEFAULT_WIDTH, 1300)
```

---

## 🚀 Hızlı Başlangıç

### 1. Configuration Manager Kullanma

```python
from configuration import ConfigurationManager, ConfigKeys

# Singleton instance'ı al
config = ConfigurationManager.get_instance()

# Değer oku (default value ile)
db_url = config.get(ConfigKeys.DATABASE_URL)
theme = config.get(ConfigKeys.UI_THEME, 'dark')

# Nested key kullan
log_file = config.get('logging.file')
```

### 2. Configuration Kaynakları

Yükleme sırası (düşük → yüksek öncelik):

1. **Defaults** - `config_manager.py` içindeki sabit değerler
2. **JSON Files** - `config/app_config.json`, `config/user_preferences.json`
3. **.env File** - `.env` dosyasındaki environment variables
4. **Database** - `app_config` tablosu (gelecek)
5. **Runtime** - `set_override()` ile set edilen değerler

### 3. Configuration Anahtarları

Tüm anahtarlar `ConfigKeys` class'ında tanımlı:

```python
from configuration import ConfigKeys

# App section
ConfigKeys.APP_NAME              # 'Aidat Plus'
ConfigKeys.APP_VERSION           # '1.3'
ConfigKeys.APP_DEBUG             # True/False
ConfigKeys.APP_ENV               # 'production', 'development'

# Database section
ConfigKeys.DATABASE_URL          # 'sqlite:///aidat_plus.db'
ConfigKeys.DATABASE_POOL_SIZE    # 10
ConfigKeys.DATABASE_ECHO         # False

# UI section
ConfigKeys.UI_THEME              # 'dark', 'light'
ConfigKeys.UI_DEFAULT_WIDTH      # 1400
ConfigKeys.UI_DEFAULT_HEIGHT     # 900

# Logging section
ConfigKeys.LOGGING_LEVEL         # 'INFO', 'DEBUG', etc.
ConfigKeys.LOGGING_FILE          # 'logs/app.log'
```

---

## 📁 Dosya Yapısı

```
AidatPlus/
├── configuration/                    # YENİ: Configuration paket
│   ├── __init__.py                  # Package exports
│   ├── config_manager.py            # ConfigurationManager sınıfı (900+ satır)
│   └── constants.py                 # ConfigKeys, ConfigDefaults, vb. (300+ satır)
│
├── config/                          # YENİ: Konfigürasyon dosyaları
│   ├── app_config.json             # Genel uygulama ayarları
│   └── user_preferences.json       # Kullanıcı tercihleri
│
├── .env.example                     # YENİ: Environment variables template
├── main.py                          # GÜNCELLENMIŞ: ConfigurationManager entegre
└── docs/
    ├── CONFIGURATION_MANAGEMENT.md  # YENİ: Kapsamlı rehber
    └── CONFIGURATION_IMPLEMENTATION.md # YENİ: Bu dosya
```

---

## 🔄 Workflow Örnekleri

### Örnek 1: Database URL'i Konfigürasyondan Alma

**Eski (Hard-coded):**
```python
db_url = "sqlite:///aidat_plus.db"
engine = create_engine(db_url)
```

**Yeni (Konfigürasyondan):**
```python
from configuration import ConfigurationManager, ConfigKeys

config = ConfigurationManager.get_instance()
db_url = config.get(ConfigKeys.DATABASE_URL)
engine = create_engine(db_url)
```

### Örnek 2: UI Tema Ayarları

**Eski (Hard-coded):**
```python
ctk.set_appearance_mode("light")
window_width = 1300
window_height = 785
```

**Yeni (Konfigürasyondan):**
```python
from configuration import ConfigurationManager, ConfigKeys

config = ConfigurationManager.get_instance()
theme = config.get(ConfigKeys.UI_THEME, 'dark')
ctk.set_appearance_mode(theme)

window_width = config.get(ConfigKeys.UI_DEFAULT_WIDTH, 1300)
window_height = config.get(ConfigKeys.UI_DEFAULT_HEIGHT, 785)
```

### Örnek 3: Logging Ayarları

**Eski (Hard-coded):**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/app.log'
)
```

**Yeni (Konfigürasyondan):**
```python
from configuration import ConfigurationManager, ConfigKeys

config = ConfigurationManager.get_instance()
logging_level = config.get(ConfigKeys.LOGGING_LEVEL, 'INFO')
logging_format = config.get(ConfigKeys.LOGGING_FORMAT)
logging_file = config.get(ConfigKeys.LOGGING_FILE, 'logs/app.log')

logging.basicConfig(
    level=getattr(logging, logging_level),
    format=logging_format,
    filename=logging_file
)
```

### Örnek 4: Controller'da Database Bağlantısı

```python
from configuration import ConfigurationManager, ConfigKeys
from database.config import create_engine, Session

class BaseController:
    def __init__(self):
        # Konfigürasyondan DB URL'i al
        config = ConfigurationManager.get_instance()
        db_url = config.get(ConfigKeys.DATABASE_URL)
        
        # Engine oluştur
        self.engine = create_engine(db_url)
        
        # Session factory oluştur
        SessionLocal = sessionmaker(bind=self.engine)
        self.session = SessionLocal()
```

### Örnek 5: Runtime Override

```python
from configuration import ConfigurationManager, ConfigKeys

config = ConfigurationManager.get_instance()

# Debug mode'u runtime'da etkinleştir
config.set_override(ConfigKeys.APP_DEBUG, True)

# Kontrol et
is_debug = config.get(ConfigKeys.APP_DEBUG)  # True
```

### Örnek 6: Kullanıcı Tercihlerini Kaydetme

```python
from configuration import ConfigurationManager

config = ConfigurationManager.get_instance()

# Kullanıcı tercihlerini kaydet
preferences = {
    'user': {
        'last_active_lojman_id': 1,
        'preferred_language': 'tr'
    },
    'ui_preferences': {
        'window_state': 'maximized',
        'sidebar_collapsed': False
    }
}

config.save_json_config('user_preferences.json', preferences)
```

---

## 🛠️ Configuration Dosyaları

### 1. `.env` Dosyası

**Template:**
```bash
cp .env.example .env
```

**İçerik:**
```
# Application
APP_ENV=production
APP_DEBUG=false

# Database
DATABASE_URL=sqlite:///aidat_plus.db
DATABASE_POOL_SIZE=10
DATABASE_ECHO=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# UI
GUI_THEME=dark
GUI_WINDOW_WIDTH=1400
GUI_WINDOW_HEIGHT=900
```

### 2. `config/app_config.json`

```json
{
  "app": {
    "name": "Aidat Plus",
    "version": "1.3",
    "debug": false,
    "env": "production"
  },
  "database": {
    "url": "sqlite:///aidat_plus.db",
    "pool_size": 10,
    "echo": false
  },
  "ui": {
    "theme": "dark",
    "default_width": 1400,
    "default_height": 900
  },
  "logging": {
    "level": "INFO",
    "file": "logs/app.log"
  },
  "features": {
    "enable_logging": true,
    "enable_backup": true,
    "enable_reports": true
  }
}
```

### 3. `config/user_preferences.json`

```json
{
  "user": {
    "last_active_lojman_id": null,
    "last_active_panel": "dashboard",
    "preferred_language": "tr"
  },
  "ui_preferences": {
    "window_state": "normal",
    "last_window_width": 1400,
    "last_window_height": 900,
    "sidebar_collapsed": false
  },
  "financial": {
    "currency": "TRY",
    "decimal_places": 2
  },
  "reports": {
    "default_date_format": "DD.MM.YYYY"
  }
}
```

---

## 📊 Configuration Manager API

### Okuma Metodları

```python
# Basit okuma
value = config.get('database.url')

# Default value ile
theme = config.get('ui.theme', 'dark')

# Nested key
config.get_nested('database.pool_size')

# Tüm config'i dictionary olarak
all_config = config.to_dict()
```

### Yazma Metodları

```python
# Konfigürasyon değeri ayarla
config.set('ui.theme', 'light')
config.set_nested('database.pool_size', 20)

# Runtime override (kalıcı olmaz, session lifetime)
config.set_override('app.debug', True)

# JSON dosyasına kaydet
preferences = {'user': {'theme': 'light'}}
config.save_json_config('user_preferences.json', preferences)
```

### Diğer Metodlar

```python
# Dosyasından JSON yükle
data = config.load_json_config('app_config.json')

# Tüm konfigürasyonu yeniden yükle
config.reload()

# Environment loaded mi kontrol et
if config.env_loaded:
    print(".env dosyası yüklendi")
```

---

## 🧪 Test Etme

### Basit Test

```python
from configuration import ConfigurationManager, ConfigKeys

config = ConfigurationManager.get_instance()
print(config.get(ConfigKeys.APP_NAME))          # Aidat Plus
print(config.get(ConfigKeys.DATABASE_URL))      # sqlite:///aidat_plus.db
print(config.get(ConfigKeys.UI_THEME))          # dark
print(config.get(ConfigKeys.LOGGING_LEVEL))     # INFO
```

### Debug Modu

```python
from configuration import ConfigurationManager

config = ConfigurationManager.get_instance()

# Tüm konfigürasyonu yazdır
import json
print(json.dumps(config.to_dict(), indent=2))
```

---

## ⚠️ Önemli Notlar

### 1. Environment Variables Önceliği

`.env` dosyasındaki değerler, JSON dosyalarındaki değerleri override eder:

```
JSON defaults < .env values < Runtime overrides
```

### 2. Sensitive Data

`.env` dosyasını **asla** git repository'ye commit etmeyin:

```bash
# .gitignore'a ekle
echo ".env" >> .gitignore
```

### 3. Production Environment

Production'da farklı ayarlar kullanın:

```
.env.production
```

### 4. Configuration Reload

`config.reload()` kullanarak yeniden yükleyebilirsiniz:

```python
config.reload()  # .env ve JSON dosyaları yeniden yüklenir
```

---

## 🔍 Troubleshooting

### Problem: Configuration Key Bulunamadı

```python
from configuration import ConfigurationManager

config = ConfigurationManager.get_instance()

# Bu hata verirse:
# ConfigError: Konfigürasyon anahtarı bulunamadı: database.url

# Çözüm 1: Default value sağla
db_url = config.get('database.url', 'sqlite:///aidat_plus.db')

# Çözüm 2: Tüm konfigürasyonu kontrol et
import json
print(json.dumps(config.to_dict(), indent=2))
```

### Problem: .env Dosyası Yüklenmedi

```python
config = ConfigurationManager.get_instance()

if not config.env_loaded:
    print(".env dosyası bulunamadı (opsiyonel)")
else:
    print(".env dosyası başarıyla yüklendi")
```

### Problem: JSON Parse Hatası

JSON dosyalarını valide et:

```bash
# Linux/Mac
python -m json.tool config/app_config.json

# Windows
python -m json.tool config/app_config.json
```

---

## 📈 İleri Konular

### Custom Configuration Provider

Özel configuration kaynağı eklemek:

```python
class CustomConfigProvider:
    def load(self) -> Dict[str, Any]:
        # Özel kaynaktan yükle (API, database, vb.)
        return {}

# ConfigurationManager'a entegre et
config = ConfigurationManager.get_instance()
custom_data = CustomConfigProvider().load()
config._merge_configs(custom_data)
```

### Configuration Validation

Konfigürasyonu valide etmek:

```python
from configuration import ConfigurationManager, ConfigKeys

config = ConfigurationManager.get_instance()

# Database URL valide mi?
db_url = config.get(ConfigKeys.DATABASE_URL)
if not db_url.startswith(('sqlite://', 'postgresql://')):
    raise ValueError("Geçersiz database URL")

# Log level valide mi?
log_level = config.get(ConfigKeys.LOGGING_LEVEL)
valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
if log_level not in valid_levels:
    raise ValueError(f"Geçersiz log level: {log_level}")
```

---

## 📝 Sonraki Adımlar

### Phase 2: Database Configuration Storage

- [ ] `AppConfig` tablosu oluştur
- [ ] `_load_database_configs()` implement et
- [ ] Runtime ayarları database'de sakla

### Phase 3: Configuration Validation

- [ ] `ConfigValidator` sınıfı oluştur
- [ ] Kritik ayarları valide et
- [ ] Hata durumlarında işleyişi kur

### Phase 4: Configuration Profiles

- [ ] Production, Development, Testing profilleri
- [ ] Profile-specific JSON dosyaları
- [ ] `load_profile()` metodunu implement et

### Phase 5: Hot Reload

- [ ] Configuration değişikliklerini izle
- [ ] Dosya değiştiğinde otomatik reload
- [ ] Listeners notifikasyon sistemi

---

## 📚 İlgili Dokümantasyon

- `docs/CONFIGURATION_MANAGEMENT.md` - Kapsamlı teknik rehber
- `configuration/config_manager.py` - Source code docstring'leri
- `configuration/constants.py` - ConfigKeys referans rehberi

---

**Versiyon**: 1.0  
**Son Güncelleme**: 29 Kasım 2025  
**Durum**: ✅ Configuration Manager v1 tamamlandı

