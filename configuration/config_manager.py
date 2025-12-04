"""Configuration Manager Module

Aidat Plus uygulaması için merkezi konfigürasyon yönetimi.
Environment variables, JSON dosyaları ve database'den konfigürasyonları yükler.

Example:
    >>> config_mgr = ConfigurationManager.get_instance()
    >>> db_url = config_mgr.get('database.url')
    >>> theme = config_mgr.get('ui.theme', 'dark')
"""

from typing import Any, Dict, Optional, TypeVar
from pathlib import Path
import json
import os
from dotenv import load_dotenv
import logging

from models.exceptions import ConfigError

logger = logging.getLogger(__name__)

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
        config_dir (Path): Konfigürasyon dosyaları dizini
        configs (Dict[str, Any]): Birleştirilmiş konfigürasyonlar
        env_loaded (bool): .env dosyası yüklendi mi
        _runtime_overrides (Dict[str, Any]): Runtime override'ları
    
    Example:
        >>> config_mgr = ConfigurationManager.get_instance()
        >>> db_url = config_mgr.get('database.url')
        >>> theme = config_mgr.get('ui.theme', 'dark')
        >>> config_mgr.set_override('app.debug', True)
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
        
        logger.info(f"ConfigurationManager başlatılıyor (config_dir={config_dir})")
        self._load_all_configs()
        logger.info("ConfigurationManager başarıyla başlatıldı")
    
    @classmethod
    def get_instance(cls, config_dir: str = 'config') -> 'ConfigurationManager':
        """Singleton instance'ı al
        
        Args:
            config_dir (str): Konfigürasyon dizini (ilk çağrıda)
        
        Returns:
            ConfigurationManager: Singleton instance
        
        Example:
            >>> config = ConfigurationManager.get_instance()
        """
        if cls._instance is None:
            cls._instance = cls(config_dir)
        return cls._instance
    
    def _load_all_configs(self) -> None:
        """Tüm konfigürasyonları yükle (override hiyerarşisi ile)
        
        Sıra:
        1. Defaults - Kod içi sabit değerler
        2. JSON Files - config/ dizinindeki JSON dosyaları
        3. .env File - Environment variables
        4. Database - app_config tablosu (varsa)
        5. Runtime - Runtime override'ları
        
        Raises:
            ConfigError: Kritik yükleme hatası
        """
        try:
            # 1. Defaults
            self._load_defaults()
            logger.debug("Varsayılan konfigürasyonlar yüklendi")
            
            # 2. JSON dosyaları
            self._load_json_configs()
            logger.debug("JSON konfigürasyonlar yüklendi")
            
            # 3. .env dosyası
            self._load_env_file()
            logger.debug("Environment variables yüklendi")
            
            # 4. Database (varsa)
            self._load_database_configs()
            
        except ConfigError as e:
            logger.error(f"Konfigürasyon yükleme hatası: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Beklenmeyen konfigürasyon hatası: {str(e)}")
            raise ConfigError(f"Konfigürasyon yükleme hatası: {str(e)}")
    
    def _load_defaults(self) -> None:
        """Varsayılan konfigürasyonları yükle
        
        Koddaki sabit değerler. Diğer tüm kaynaklar bunu override edebilir.
        """
        self.configs = {
            'app': {
                'name': 'Aidat Plus',
                'version': '1.3',
                'debug': False,
                'env': 'production',
                'organization': 'Lojman Yönetimi',
                'support_email': 'support@aidatplus.local'
            },
            'database': {
                'type': 'sqlite',
                'url': 'sqlite:///aidat_plus.db',
                'pool_size': 10,
                'pool_recycle': 3600,
                'echo': False,
                'check_same_thread': False
            },
            'ui': {
                'theme': 'light',
                'default_width': 1400,
                'default_height': 900,
                'font_size': 11,
                'color_scheme': 'modern'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/app.log',
                'max_bytes': 10485760,
                'backup_count': 5
            },
            'features': {
                'enable_logging': True,
                'enable_backup': True,
                'enable_reports': True,
                'enable_charts': True
            }
        }
    
    def _load_json_configs(self) -> None:
        """JSON konfigürasyon dosyalarını yükle
        
        config/ dizinindeki JSON dosyalarını sırayla yükler:
        1. app_config.json - Genel uygulama ayarları
        2. user_preferences.json - Kullanıcı tercihleri
        3. kategoriler.json - Kategori sistemi
        
        Raises:
            ConfigError: JSON parse veya okuma hatası
        """
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
                        logger.debug(f"JSON yüklendi: {filename}")
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse hatası ({filename}): {str(e)}")
                    raise ConfigError(f"JSON parse hatası ({filename}): {str(e)}")
                except IOError as e:
                    logger.warning(f"JSON okuma hatası ({filename}): {str(e)}")
                    raise ConfigError(f"JSON okuma hatası ({filename}): {str(e)}")
            else:
                logger.debug(f"JSON dosyası bulunamadı: {filename}")
    
    def _load_env_file(self) -> None:
        """Environment variables'ları yükle (.env dosyasından)
        
        .env dosyasını yükler ve önemli env variables'ları
        konfigürasyona ekler.
        """
        env_file = Path('.env')
        
        if env_file.exists():
            try:
                load_dotenv(env_file)
                self.env_loaded = True
                logger.debug(".env dosyası yüklendi")
                
                # Önemli environment variables'ları konfigürasyona ekle
                self._apply_env_overrides()
            except Exception as e:
                logger.warning(f".env yükleme hatası: {str(e)}")
        else:
            logger.debug(".env dosyası bulunamadı (opsiyonel)")
    
    def _apply_env_overrides(self) -> None:
        """Environment variables'ları konfigürasyona uygula
        
        .env dosyasındaki önemli değişkenleri konfigürasyona ekler.
        Override hiyerarşisinin en üstünde yer alır.
        """
        env_mapping = {
            'DATABASE_URL': 'database.url',
            'DATABASE_POOL_SIZE': 'database.pool_size',
            'DATABASE_ECHO': 'database.echo',
            'LOG_LEVEL': 'logging.level',
            'APP_ENV': 'app.env',
            'APP_DEBUG': 'app.debug',
            'GUI_THEME': 'ui.theme',
            'GUI_WINDOW_WIDTH': 'ui.default_width',
            'GUI_WINDOW_HEIGHT': 'ui.default_height'
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                parsed_value = self._parse_value(value)
                self.set_nested(config_key, parsed_value)
                logger.debug(f"Env override: {env_var} → {config_key}")
    
    def _load_database_configs(self) -> None:
        """Database'den dinamik konfigürasyonları yükle
        
        app_config tablosundan runtime ayarlarını yükler.
        (Şu an kullanılmıyor, gelecek sürümler için)
        """
        try:
            from database.config import get_db
            from models.base import Ayar
            import json

            try:
                db = get_db()
            except Exception as e:
                logger.debug(f"DB bağlantısı oluşturulurken hata: {e}")
                return

            try:
                ayarlar = db.query(Ayar).all()
            except Exception as e:
                logger.warning(f"Veritabanından ayarlar alınırken hata: {e}")
                return
            finally:
                try:
                    db.close()
                except Exception:
                    pass

            for ayar in ayarlar:
                if not getattr(ayar, 'anahtar', None):
                    continue
                key = ayar.anahtar
                value = ayar.deger

                if value is None:
                    parsed = None
                else:
                    s = str(value).strip()
                    # Eğer JSON içerikse JSON parse et
                    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
                        try:
                            parsed = json.loads(s)
                        except Exception:
                            parsed = s
                    else:
                        parsed = self._parse_value(s)

                try:
                    # Nested anahtarlar varsa set_nested kullan
                    self.set_nested(key, parsed)
                except Exception as e:
                    logger.warning(f"Ayar '{key}' yüklenirken hata: {e}")
                    # continue with next key
                    continue

        except Exception as e:
            logger.warning(f"_load_database_configs hatası: {e}")
            # Fail silent — DB configs are optional
            return
    
    def _merge_configs(self, new_config: Dict[str, Any], 
                      path: str = '') -> None:
        """Yeni konfigürasyonu mevcut konfigürasyonla birleştir
        
        Nested dictionaries'i recursive olarak merge eder.
        
        Args:
            new_config (Dict): Yeni konfigürasyon
            path (str): Nested path (internal)
        
        Example:
            >>> config._merge_configs({'database': {'echo': True}})
        """
        for key, value in new_config.items():
            full_key = f"{path}.{key}" if path else key
            
            if isinstance(value, dict) and full_key in self.configs:
                if isinstance(self.configs[full_key], dict):
                    self._merge_configs(value, full_key)
                else:
                    self.set_nested(full_key, value)
            else:
                self.set_nested(full_key, value)
    
    def get(self, key: str, default: T = None) -> T:
        """Konfigürasyon değeri al
        
        Override hiyerarşisine göre değer alır:
        1. Runtime overrides
        2. Yapılandırılmış configs
        3. Default value (sağlanmışsa)
        
        Args:
            key (str): Konfigürasyon anahtarı (nested: "database.url")
            default (T): Varsayılan değer (bulunamadıysa dönülür)
        
        Returns:
            T: Konfigürasyon değeri
        
        Raises:
            ConfigError: Anahtar bulunamadı ve default yoksa
        
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
                logger.debug(f"Config anahtarı bulunamadı: {key}, default kullanılıyor")
                return default
            
            logger.error(f"Config anahtarı bulunamadı ve default yok: {key}")
            raise ConfigError(f"Konfigürasyon anahtarı bulunamadı: {key}")
    
    def get_nested(self, key: str, default: Any = None) -> Any:
        """Nested konfigürasyon değeri al (get() ile aynı)
        
        Args:
            key (str): Nested anahtarı ("database.url" gibi)
            default (Any): Varsayılan değer
        
        Returns:
            Any: Konfigürasyon değeri
        """
        return self.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Konfigürasyon değeri ayarla
        
        Args:
            key (str): Konfigürasyon anahtarı
            value (Any): Yeni değer
        
        Example:
            >>> config.set('ui.theme', 'light')
        """
        self.set_nested(key, value)
    
    def set_nested(self, key: str, value: Any) -> None:
        """Nested konfigürasyon değeri ayarla
        
        Nested anahtarlar için yeni dictionary'ler oluşturur.
        
        Args:
            key (str): Nested anahtarı ("database.url" gibi)
            value (Any): Yeni değer
        
        Example:
            >>> config.set_nested('database.url', 'sqlite:///new.db')
        """
        keys = key.split('.')
        config = self.configs
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"Config set: {key} = {value}")
    
    def set_override(self, key: str, value: Any) -> None:
        """Runtime override ayarla (en yüksek öncelik)
        
        Runtime'da set edilen override'lar, tüm diğer kaynakları override eder.
        Application lifetime'ında geçerlidir.
        
        Args:
            key (str): Konfigürasyon anahtarı
            value (Any): Override değeri
        
        Example:
            >>> config.set_override('app.debug', True)
        """
        self._runtime_overrides[key] = value
        logger.debug(f"Config override: {key} = {value}")
    
    def save_json_config(self, filename: str, data: Dict[str, Any]) -> None:
        """Konfigürasyonu JSON dosyasına kaydet
        
        Args:
            filename (str): Dosya adı (config dizininde)
            data (Dict): Kaydetmek için veri
        
        Raises:
            ConfigError: Dosya yazma hatası
        
        Example:
            >>> prefs = {'user': {'theme': 'light'}}
            >>> config.save_json_config('user_preferences.json', prefs)
        """
        filepath = self.config_dir / filename
        
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Config kaydedildi: {filename}")
        except IOError as e:
            logger.error(f"Config yazma hatası: {str(e)}")
            raise ConfigError(f"Konfigürasyon yazma hatası: {str(e)}")
    
    def load_json_config(self, filename: str) -> Dict[str, Any]:
        """JSON dosyasından konfigürasyon yükle
        
        Args:
            filename (str): Dosya adı (config dizininde)
        
        Returns:
            Dict: Konfigürasyon verisi
        
        Raises:
            ConfigError: Dosya okuma hatası
        
        Example:
            >>> data = config.load_json_config('app_config.json')
        """
        filepath = self.config_dir / filename
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config dosyası bulunamadı: {filename}")
            raise ConfigError(f"Konfigürasyon dosyası bulunamadı: {filename}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse hatası: {str(e)}")
            raise ConfigError(f"Konfigürasyon parse hatası: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Tüm konfigürasyonu dictionary olarak al
        
        Returns:
            Dict: Tam konfigürasyon (runtime overrides dahil)
        
        Example:
            >>> full_config = config.to_dict()
            >>> print(full_config)
        """
        # Runtime override'ları merge et
        result = self.configs.copy()
        for key, value in self._runtime_overrides.items():
            self._set_nested_dict(result, key, value)
        return result
    
    def _set_nested_dict(self, d: Dict, key: str, value: Any) -> None:
        """Nested dictionary'ye değer ayarla (helper)"""
        keys = key.split('.')
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
    
    def reload(self) -> None:
        """Tüm konfigürasyonları yeniden yükle
        
        Diskte yapılan değişiklikleri uygulamak için kullanılır.
        Runtime overrides'ler silinir.
        
        Example:
            >>> config.reload()  # .env veya JSON dosyası değişti
        """
        logger.info("Configuration yeniden yükleniyor...")
        self.configs.clear()
        self._runtime_overrides.clear()
        self._load_all_configs()
        logger.info("Configuration yeniden yükleme tamamlandı")
    
    @staticmethod
    def _parse_value(value: str) -> Any:
        """String değeri uygun tipe çevir
        
        Args:
            value (str): String değer
        
        Returns:
            Any: Dönüştürülen değer (bool, int, float, veya str)
        
        Example:
            >>> ConfigurationManager._parse_value('true')
            True
            >>> ConfigurationManager._parse_value('10')
            10
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
