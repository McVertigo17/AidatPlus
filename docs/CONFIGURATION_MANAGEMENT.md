# Configuration Management Rehberi

Aidat Plus uygulaması için kapsamlı Configuration Management sistemi.

---

## 📋 İçerik

1. [Genel Bakış](#genel-bakış)
2. [Configuration Kaynakları](#configuration-kaynakları)
3. [Mimari ve Tasarım](#mimari-ve-tasarım)
4. [Configuration Modeli](#configuration-modeli)
5. [Loading Mekanizması](#loading-mekanizması)
6. [Best Practices](#best-practices)
7. [Kullanım Örnekleri](#kullanım-örnekleri)
8. [Environment-Spesifik Konfigürasyonlar](#environment-spesifik-konfigürasyonlar)
9. [Troubleshooting](#troubleshooting)

---

## Genel Bakış

Configuration Management, Aidat Plus'ın ayarlarını, tercihlerini ve konfigürasyonlarını merkezi bir yerden yönetmesini sağlayan sistemdir.

### Amaçlar

- 🎯 Tüm ayarları merkezi olarak yönetmek
- 🎯 Dış faktörlere (environment) göre uyum sağlamak
- 🎯 Kullanıcı tercihleri kaydetmek ve geri yüklemek
- 🎯 Application state'i sürdürmek
- 🎯 Güvenli credential depolama
- 🎯 Kolay test etme ve debug

### Kapsamı

| Alan | Kapsam |
|------|--------|
| **Veritabanı** | Bağlantı ayarları, path, pool size |
| **UI** | Tema, pencere boyutu, son açılan dosya |
| **Kullanıcı Tercihleri** | Dil, görüntü seçenekleri, varsayılan değerler |
| **Lojman Ayarları** | Mevcut lojman, para birimi, yıl ayarları |
| **Finansal** | Varsayılan hesaplar, kategori ayarları |
| **Logging** | Log seviyesi, output yolları |
| **Yedekleme** | Backup ayarları, otomatik yedekleme |
| **API/External** | Harici sistem bağlantıları (gelecek) |

---

## Configuration Kaynakları

### 1. **Environment Variables** (`.env` dosyası)

Hassas bilgiler ve environment-spesifik ayarlar:

```
# .env dosyası (gitignore'da)
DATABASE_URL=sqlite:///aidat_plus.db
DATABASE_POOL_SIZE=10
DATABASE_ECHO=false

LOG_LEVEL=INFO
LOG_FILE=logs/app.log

APP_ENV=production
APP_DEBUG=false

# GUI Ayarları
GUI_THEME=dark
GUI_WINDOW_WIDTH=1400
GUI_WINDOW_HEIGHT=900

# Güvenlik
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key

# Yedekleme
BACKUP_INTERVAL=86400
BACKUP_PATH=backups/
AUTO_BACKUP_ENABLED=true
```

### 2. **JSON Configuration Dosyaları**

**`config/app_config.json`** - Genel uygulama ayarları:

```json
{
  "app": {
    "name": "Aidat Plus",
    "version": "1.3",
    "organization": "Lojman Yönetimi",
    "support_email": "support@aidatplus.local"
  },
  "database": {
    "type": "sqlite",
    "path": "aidat_plus.db",
    "pool_size": 10,
    "pool_recycle": 3600,
    "echo": false,
    "check_same_thread": false
  },
  "ui": {
    "theme": "dark",
    "default_width": 1400,
    "default_height": 900,
    "font_size": 11,
    "color_scheme": "modern"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/app.log",
    "max_bytes": 10485760,
    "backup_count": 5
  },
  "features": {
    "enable_logging": true,
    "enable_backup": true,
    "enable_reports": true,
    "enable_charts": true
  }
}
```

**`config/user_preferences.json`** - Kullanıcı tercihleri:

```json
{
  "user": {
    "last_active_lojman_id": 1,
    "last_active_panel": "dashboard",
    "preferred_language": "tr"
  },
  "ui_preferences": {
    "window_state": "maximized",
    "last_window_width": 1400,
    "last_window_height": 900,
    "sidebar_collapsed": false
  },
  "financial": {
    "currency": "TRY",
    "decimal_places": 2,
    "default_account_id": null
  },
  "reports": {
    "default_date_format": "DD.MM.YYYY",
    "include_zero_values": false
  }
}
```

**`config/kategoriler.json`** - Kategori sistemi (mevcut):

```json
{
  "ana_kategoriler": [
    {
      "id": "gelir_001",
      "ad": "Gelirler",
      "tip": "gelir",
      "alt_kategoriler": []
    }
  ]
}
```

### 3. **SQLite Ayar Tablosu**

Dinamik ayarlar için database'de tablo:

```python
class AppConfig(Base):
    """Uygulama konfigürasyon tablosu
    
    Bu tablo runtime'da değiştirilmesi gereken ayarları depolar.
    JSON formatında değerler tutabilir.
    """
    __tablename__ = "app_config"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    config_key: Mapped[str] = mapped_column(String(255), unique=True)
    config_value: Mapped[str] = mapped_column(Text)
    data_type: Mapped[str] = mapped_column(String(50))  # string, int, float, bool, json
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## Mimari ve Tasarım

### Katmanlar

```
┌────────────────────────────────┐
│   Application (main.py)        │ ← Konfigürasyonu kullanır
└───────────────┬────────────────┘
                │
┌───────────────▼────────────────┐
│  ConfigurationManager          │ ← Merkezi yönetim
│  - Load configs               │
│  - Merge configurations       │
│  - Override hierarchy         │
└───────────────┬────────────────┘
                │
      ┌─────────┼─────────┐
      │         │         │
┌─────▼──┐  ┌──▼────┐  ┌─▼──────┐
│ .env   │  │JSON   │  │Database│
│Files   │  │Files  │  │(SQLite)│
└────────┘  └───────┘  └────────┘
```

### Override Hiyerarşisi

Düşük → Yüksek Öncelik:

1. **Defaults** - Kod içinde sabit değerler
2. **JSON Config Files** - `config/*.json`
3. **Database** - `app_config` tablosu
4. **Environment Variables** - `.env` dosyası
5. **Runtime Override** - Runtime'da set edilen değerler (UI'dan)

### Tasarım Desenleri

#### Singleton Pattern

```python
class ConfigurationManager:
    _instance: Optional['ConfigurationManager'] = None
    
    @classmethod
    def get_instance(cls) -> 'ConfigurationManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

#### Registry Pattern

```python
class ConfigRegistry:
    """Konfigürasyon registry'si"""
    
    _configs: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, key: str, value: Any) -> None:
        cls._configs[key] = value
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        return cls._configs.get(key, default)
```

---

## Configuration Modeli

### ConfigurationManager Sınıfı

```python
from typing import Any, Dict, Optional, Type, TypeVar
from pathlib import Path
import json
import os
from dotenv import load_dotenv
from models.exceptions import ConfigError

T = TypeVar('T')

class ConfigurationManager:
    """Uygulama konfigürasyon yöneticisi
    
    Tüm uygulamanın konfigürasyonunu yönetir:
    - Environment variables (.env)
    - JSON dosyaları (config/)
    - Database ayarları
    - Runtime override'ları
    
    Singleton pattern kullanır.
    
    Attributes:
        _instance (ConfigurationManager): Singleton instance
        configs (Dict[str, Any]): Birleştirilmiş konfigürasyonlar
        env_loaded (bool): .env dosyası yüklendi mi
    
    Example:
        >>> config_mgr = ConfigurationManager.get_instance()
        >>> db_url = config_mgr.get('database.url')
        >>> log_level = config_mgr.get('logging.level', 'INFO')
    """
    
    _instance: Optional['ConfigurationManager'] = None
    
    def __init__(self, config_dir: str = 'config') -> None:
        """ConfigurationManager'ı başlat
        
        Args:
            config_dir (str): Konfigürasyon dosyaları dizini
        
        Raises:
            ConfigError: Kritik konfigürasyon dosyası bulunamadığında
        """
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Any] = {}
        self.env_loaded = False
        self._runtime_overrides: Dict[str, Any] = {}
        
        self._load_all_configs()
    
    @classmethod
    def get_instance(cls, config_dir: str = 'config') -> 'ConfigurationManager':
        """Singleton instance'ı al
        
        Args:
            config_dir (str): Konfigürasyon dizini (ilk çağrıda)
        
        Returns:
            ConfigurationManager: Singleton instance
        """
        if cls._instance is None:
            cls._instance = cls(config_dir)
        return cls._instance
    
    def _load_all_configs(self) -> None:
        """Tüm konfigürasyonları yükle (override hiyerarşisi ile)"""
        try:
            # 1. Defaults
            self._load_defaults()
            
            # 2. JSON dosyaları
            self._load_json_configs()
            
            # 3. .env dosyası
            self._load_env_file()
            
            # 4. Database (varsa)
            self._load_database_configs()
            
        except Exception as e:
            raise ConfigError(f"Konfigürasyon yükleme hatası: {str(e)}")
    
    def _load_defaults(self) -> None:
        """Varsayılan konfigürasyonları yükle"""
        self.configs = {
            'app': {
                'name': 'Aidat Plus',
                'version': '1.3',
                'debug': False,
                'env': 'production'
            },
            'database': {
                'url': 'sqlite:///aidat_plus.db',
                'pool_size': 10,
                'echo': False
            },
            'ui': {
                'theme': 'dark',
                'width': 1400,
                'height': 900
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/app.log'
            }
        }
    
    def _load_json_configs(self) -> None:
        """JSON konfigürasyon dosyalarını yükle"""
        config_files = [
            'app_config.json',
            'user_preferences.json',
            'kategoriler.json'
        ]
        
        for filename in config_files:
            filepath = self.config_dir / filename
            
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._merge_configs(data)
                except (json.JSONDecodeError, IOError) as e:
                    raise ConfigError(f"JSON yükleme hatası ({filename}): {str(e)}")
    
    def _load_env_file(self) -> None:
        """Environment variables'ları yükle (.env dosyasından)"""
        env_file = Path('.env')
        
        if env_file.exists():
            load_dotenv(env_file)
            self.env_loaded = True
            
            # Önemli environment variables'ları konfigürasyona ekle
            self._apply_env_overrides()
    
    def _apply_env_overrides(self) -> None:
        """Environment variables'ları konfigürasyona uygula"""
        env_mapping = {
            'DATABASE_URL': 'database.url',
            'LOG_LEVEL': 'logging.level',
            'APP_ENV': 'app.env',
            'APP_DEBUG': 'app.debug',
            'GUI_THEME': 'ui.theme'
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                self.set_nested(config_key, self._parse_value(value))
    
    def _load_database_configs(self) -> None:
        """Database'den dinamik konfigürasyonları yükle"""
        # Bu, ConfigurationManager başlatıldıktan sonra
        # database session açılmışsa yapılır
        pass
    
    def _merge_configs(self, new_config: Dict[str, Any], 
                      path: str = '') -> None:
        """Yeni konfigürasyonu mevcut konfigürasyonla birleştir
        
        Args:
            new_config (Dict): Yeni konfigürasyon
            path (str): Nested path
        """
        for key, value in new_config.items():
            full_key = f"{path}.{key}" if path else key
            
            if isinstance(value, dict) and full_key in self.configs:
                self._merge_configs(value, full_key)
            else:
                self.set_nested(full_key, value)
    
    def get(self, key: str, default: T = None) -> T:
        """Konfigürasyon değeri al
        
        Args:
            key (str): Konfigürasyon anahtarı (nested: "database.url")
            default (T): Varsayılan değer
        
        Returns:
            T: Konfigürasyon değeri
        
        Example:
            >>> config = ConfigurationManager.get_instance()
            >>> db_url = config.get('database.url')
            >>> theme = config.get('ui.theme', 'dark')
        """
        # 1. Runtime override'lardan kontrol et
        if key in self._runtime_overrides:
            return self._runtime_overrides[key]
        
        # 2. Nested key'leri parse et
        keys = key.split('.')
        value = self.configs
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise ConfigError(f"Konfigürasyon anahtarı bulunamadı: {key}")
    
    def get_nested(self, key: str, default: Any = None) -> Any:
        """Nested konfigürasyon değeri al (get() ile aynı)"""
        return self.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Konfigürasyon değeri ayarla
        
        Args:
            key (str): Konfigürasyon anahtarı
            value (Any): Yeni değer
        """
        self.set_nested(key, value)
    
    def set_nested(self, key: str, value: Any) -> None:
        """Nested konfigürasyon değeri ayarla
        
        Args:
            key (str): Nested anahtarı ("database.url" gibi)
            value (Any): Yeni değer
        """
        keys = key.split('.')
        config = self.configs
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def set_override(self, key: str, value: Any) -> None:
        """Runtime override ayarla (en yüksek öncelik)
        
        Args:
            key (str): Konfigürasyon anahtarı
            value (Any): Override değeri
        """
        self._runtime_overrides[key] = value
    
    def save_json_config(self, filename: str, data: Dict[str, Any]) -> None:
        """Konfigürasyonu JSON dosyasına kaydet
        
        Args:
            filename (str): Dosya adı (config dizininde)
            data (Dict): Kaydetmek için veri
        
        Raises:
            ConfigError: Dosya yazma hatası
        """
        filepath = self.config_dir / filename
        
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise ConfigError(f"Konfigürasyon yazma hatası: {str(e)}")
    
    def load_json_config(self, filename: str) -> Dict[str, Any]:
        """JSON dosyasından konfigürasyon yükle
        
        Args:
            filename (str): Dosya adı
        
        Returns:
            Dict: Konfigürasyon verisi
        
        Raises:
            ConfigError: Dosya okuma hatası
        """
        filepath = self.config_dir / filename
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ConfigError(f"Konfigürasyon okuma hatası: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Tüm konfigürasyonu dictionary olarak al
        
        Returns:
            Dict: Tam konfigürasyon
        """
        return self.configs.copy()
    
    def reload(self) -> None:
        """Tüm konfigürasyonları yeniden yükle"""
        self.configs.clear()
        self._runtime_overrides.clear()
        self._load_all_configs()
    
    @staticmethod
    def _parse_value(value: str) -> Any:
        """String değeri uygun tipe çevir
        
        Args:
            value (str): String değer
        
        Returns:
            Any: Dönüştürülen değer
        """
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        elif value.isdigit():
            return int(value)
        else:
            try:
                return float(value)
            except ValueError:
                return value
```

---

## Loading Mekanizması

### Application Startup Flow

```
1. main.py başlatılır
   ↓
2. ConfigurationManager.get_instance() çağrılır
   ↓
3. _load_all_configs() çalışır:
   ├─ _load_defaults()      ← Kod içi sabitler
   ├─ _load_json_configs()  ← JSON dosyaları
   ├─ _load_env_file()      ← .env dosyası
   └─ _load_database_configs() ← Database (varsa)
   ↓
4. Controllers/UI'lar konfigürasyonu kullanır
   ↓
5. Runtime'da override'lar uygulanabilir
```

### Örnek: main.py Entegrasyonu

```python
from configuration.config_manager import ConfigurationManager
from database.config import create_engine, Session
import logging

def main():
    # 1. Configuration Manager başlat
    config_mgr = ConfigurationManager.get_instance()
    
    # 2. Logging konfigürasyonunu uygula
    setup_logging(config_mgr)
    
    # 3. Database'i konfigüre et
    db_url = config_mgr.get('database.url')
    engine = create_engine(db_url)
    
    # 4. UI başlat
    app = AidatPlusApp(config_mgr)
    app.mainloop()

def setup_logging(config_mgr: ConfigurationManager):
    """Logging'i konfigürasyona göre ayarla"""
    log_level = config_mgr.get('logging.level', 'INFO')
    log_file = config_mgr.get('logging.file', 'logs/app.log')
    
    logger = logging.getLogger('aidatplus')
    logger.setLevel(getattr(logging, log_level))
    
    # Handler'ları ayarla
    # ...
```

---

## Best Practices

### 1. **Configuration Keys Standardı**

Nested keys kullan:

```python
# ✅ İyi
config.get('database.url')
config.get('ui.theme')
config.get('logging.level')

# ❌ Kötü
config.get('db_url')
config.get('theme')
```

### 2. **Constant Definition**

Configuration key'lerini constant olarak tanımla:

```python
# config/constants.py
class ConfigKeys:
    """Configuration anahtarları"""
    
    # Database
    DATABASE_URL = 'database.url'
    DATABASE_POOL_SIZE = 'database.pool_size'
    
    # UI
    UI_THEME = 'ui.theme'
    UI_WIDTH = 'ui.width'
    
    # Logging
    LOG_LEVEL = 'logging.level'
    LOG_FILE = 'logging.file'

# Kullanım
config.get(ConfigKeys.DATABASE_URL)
```

### 3. **Default Values**

Her zaman default value sağla:

```python
# ✅ İyi
theme = config.get('ui.theme', 'dark')
log_level = config.get('logging.level', 'INFO')

# ❌ Kötü (exception riski)
theme = config.get('ui.theme')
```

### 4. **Sensitive Data Handling**

Hassas bilgiler .env'de sakla:

```bash
# .env dosyası (gitignore'da)
DATABASE_PASSWORD=secure_password
API_KEY=secret_api_key
ENCRYPTION_KEY=secret_encryption_key
```

```python
# Kullanım
password = config.get('database.password')  # .env'den yüklenir
```

### 5. **Configuration Validation**

Yüklenen konfigürasyonları valide et:

```python
class ConfigValidator:
    """Configuration validasyonu"""
    
    @staticmethod
    def validate_database_config(config: Dict) -> bool:
        """Database konfigürasyonu valide et"""
        required = ['url', 'pool_size']
        
        for key in required:
            if key not in config.get('database', {}):
                raise ConfigError(f"Eksik ayar: database.{key}")
        
        return True
    
    @staticmethod
    def validate_all(config: ConfigurationManager) -> bool:
        """Tüm konfigürasyonu valide et"""
        try:
            ConfigValidator.validate_database_config(config.to_dict())
            ConfigValidator.validate_ui_config(config.to_dict())
            ConfigValidator.validate_logging_config(config.to_dict())
            return True
        except ConfigError as e:
            logging.error(f"Konfigürasyon validasyonu başarısız: {e}")
            return False
```

### 6. **Configuration Profiles**

Farklı environment'lar için profiller:

```
config/
├── app_config.json        # Tüm envs için genel
├── app_config.dev.json    # Development specific
├── app_config.prod.json   # Production specific
└── app_config.test.json   # Testing specific
```

```python
def load_profile(env: str) -> None:
    """Environment'a göre profil yükle"""
    config_mgr = ConfigurationManager.get_instance()
    
    profile_file = f'app_config.{env}.json'
    try:
        data = config_mgr.load_json_config(profile_file)
        config_mgr._merge_configs(data)
    except ConfigError:
        logging.warning(f"Profile bulunamadı: {profile_file}")
```

### 7. **Hot Reload Prevention**

Runtime'da tehlikeli override'ları engelle:

```python
class ImmutableConfigKeys:
    """Değiştirilemez konfigürasyon anahtarları"""
    
    PROTECTED_KEYS = [
        'database.url',
        'database.type',
        'app.version'
    ]
    
    @staticmethod
    def is_protected(key: str) -> bool:
        return key in ImmutableConfigKeys.PROTECTED_KEYS

# Kullanım
if ImmutableConfigKeys.is_protected(key):
    raise ConfigError(f"Korumalı ayar değiştirilemez: {key}")
```

---

## Kullanım Örnekleri

### Örnek 1: Controller'da Database URL Alma

```python
from configuration.config_manager import ConfigurationManager

class BaseController:
    def __init__(self):
        config_mgr = ConfigurationManager.get_instance()
        self.db_url = config_mgr.get('database.url')
        self.session = self.create_session()
```

### Örnek 2: UI'da Tema Yükleme

```python
class AidatPlusApp:
    def __init__(self):
        self.config = ConfigurationManager.get_instance()
        self.theme = self.config.get('ui.theme', 'dark')
        self.apply_theme()
    
    def apply_theme(self):
        if self.theme == 'dark':
            ctk.set_appearance_mode('dark')
        else:
            ctk.set_appearance_mode('light')
```

### Örnek 3: User Preference Kaydetme

```python
class SettingsPanel:
    def save_preferences(self):
        config_mgr = ConfigurationManager.get_instance()
        
        # Kullanıcı tercihlerini kaydet
        preferences = {
            'user': {
                'last_active_lojman_id': self.selected_lojman_id,
                'preferred_language': 'tr'
            }
        }
        
        config_mgr.save_json_config('user_preferences.json', preferences)
```

### Örnek 4: Runtime Override

```python
def toggle_debug_mode():
    config_mgr = ConfigurationManager.get_instance()
    
    # Runtime override (permanent olmaz)
    config_mgr.set_override('app.debug', True)
    
    # Kontrol et
    is_debug = config_mgr.get('app.debug')
```

---

## Environment-Spesifik Konfigürasyonlar

### Development Environment

```json
{
  "app": {
    "debug": true,
    "env": "development"
  },
  "database": {
    "echo": true,
    "pool_size": 5
  },
  "logging": {
    "level": "DEBUG"
  }
}
```

### Production Environment

```json
{
  "app": {
    "debug": false,
    "env": "production"
  },
  "database": {
    "echo": false,
    "pool_size": 20,
    "pool_recycle": 3600
  },
  "logging": {
    "level": "WARNING"
  }
}
```

### Testing Environment

```json
{
  "app": {
    "debug": true,
    "env": "testing"
  },
  "database": {
    "url": "sqlite:///:memory:",
    "echo": false
  },
  "logging": {
    "level": "INFO"
  }
}
```

---

## Troubleshooting

### Problem 1: Configuration Key Bulunamadı

**Hata**: `ConfigError: Konfigürasyon anahtarı bulunamadı: database.url`

**Çözüm**:
1. JSON dosyalarını kontrol et
2. .env dosyasını kontrol et
3. Default values var mı kontrol et
4. `config_mgr.to_dict()` ile bütün config'i listele

```python
config_mgr = ConfigurationManager.get_instance()
print(config_mgr.to_dict())
```

### Problem 2: Environment Variables Yüklenmemiş

**Hata**: `.env` dosyası yüklenmiyor

**Çözüm**:
1. `.env` dosyasının project root'ta olduğunu kontrol et
2. Dosya ismini kontrol et (`.env` olmalı)
3. Dosya format'ını kontrol et

```python
# Debug: env_loaded flag'ı kontrol et
config_mgr = ConfigurationManager.get_instance()
print(f"ENV loaded: {config_mgr.env_loaded}")
```

### Problem 3: JSON Parse Hatası

**Hata**: `ConfigError: JSON yükleme hatası (app_config.json)`

**Çözüm**:
1. JSON syntax'ı valide et (JSONLint kullan)
2. UTF-8 encoding kontrol et
3. Özel karakterler escape et

```python
# Validation
import json

with open('config/app_config.json', 'r') as f:
    json.load(f)  # Syntax hatası varsa hata verir
```

### Problem 4: Override Çalışmıyor

**Hata**: `set_override()` sonrası değer değişmiyor

**Çözüm**:
1. `get()` yerine `get_nested()` veya doğru anahtarı kullan
2. Override'ı set etmeden önce ConfigurationManager başlatıldığını kontrol et

```python
# Doğru yol
config_mgr = ConfigurationManager.get_instance()
config_mgr.set_override('ui.theme', 'light')
theme = config_mgr.get('ui.theme')  # 'light' döner
```

---

## Özet

| Aspekt | Detay |
|--------|-------|
| **Kaynak** | .env, JSON, Database |
| **Hiyerarşi** | Defaults → JSON → Env → Database → Runtime |
| **Pattern** | Singleton + Registry |
| **Best Practice** | Nested keys, default values, constants |
| **Security** | Sensitive data .env'de, gitignore |
| **Testing** | Profile-based configuration |

---

**Son Güncelleme**: 29 Kasım 2025 (v1.3)  
**Dokümantasyon Versiyonu**: 1.0

