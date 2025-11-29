"""Configuration Keys Constants

Uygulamanın tüm konfigürasyon anahtarlarını bir yerde tanımlar.
Bu sabitler, configuration key'lerin yazım hatalarını engellemek için kullanılır.

Example:
    >>> from configuration.constants import ConfigKeys
    >>> db_url = config.get(ConfigKeys.DATABASE_URL)
"""


class ConfigKeys:
    """Configuration anahtarları (constants)
    
    Uygulamadaki tüm configuration key'leri buradan referans edilir.
    Typo'dan korunmak için centralized constant tanımlaması.
    """
    
    # ==================== APP SECTION ====================
    
    APP_NAME = 'app.name'
    """Uygulama adı (str): 'Aidat Plus'"""
    
    APP_VERSION = 'app.version'
    """Uygulama versiyonu (str): '1.3'"""
    
    APP_DEBUG = 'app.debug'
    """Debug modu (bool): True/False"""
    
    APP_ENV = 'app.env'
    """Environment tipi (str): 'development', 'production', 'testing'"""
    
    APP_ORGANIZATION = 'app.organization'
    """Organizasyon adı (str)"""
    
    APP_SUPPORT_EMAIL = 'app.support_email'
    """Destek e-maili (str)"""
    
    # ==================== DATABASE SECTION ====================
    
    DATABASE_TYPE = 'database.type'
    """Veritabanı türü (str): 'sqlite'"""
    
    DATABASE_URL = 'database.url'
    """Veritabanı bağlantı URL'i (str)"""
    
    DATABASE_POOL_SIZE = 'database.pool_size'
    """Bağlantı pool boyutu (int)"""
    
    DATABASE_POOL_RECYCLE = 'database.pool_recycle'
    """Pool recycle süresi saniye (int)"""
    
    DATABASE_ECHO = 'database.echo'
    """SQL sorgu logging (bool)"""
    
    DATABASE_CHECK_SAME_THREAD = 'database.check_same_thread'
    """SQLite same thread check (bool)"""
    
    # ==================== UI SECTION ====================
    
    UI_THEME = 'ui.theme'
    """Tema (str): 'dark', 'light'"""
    
    UI_DEFAULT_WIDTH = 'ui.default_width'
    """Varsayılan pencere genişliği (int)"""
    
    UI_DEFAULT_HEIGHT = 'ui.default_height'
    """Varsayılan pencere yüksekliği (int)"""
    
    UI_FONT_SIZE = 'ui.font_size'
    """Font boyutu (int)"""
    
    UI_COLOR_SCHEME = 'ui.color_scheme'
    """Renk şeması (str): 'modern', 'classic'"""
    
    # ==================== LOGGING SECTION ====================
    
    LOGGING_LEVEL = 'logging.level'
    """Log seviyesi (str): 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'"""
    
    LOGGING_FORMAT = 'logging.format'
    """Log format string (str)"""
    
    LOGGING_FILE = 'logging.file'
    """Log dosya yolu (str)"""
    
    LOGGING_MAX_BYTES = 'logging.max_bytes'
    """Maximum log dosya boyutu (int)"""
    
    LOGGING_BACKUP_COUNT = 'logging.backup_count'
    """Yedek log dosya sayısı (int)"""
    
    # ==================== FEATURES SECTION ====================
    
    FEATURES_ENABLE_LOGGING = 'features.enable_logging'
    """Logging özelliği (bool)"""
    
    FEATURES_ENABLE_BACKUP = 'features.enable_backup'
    """Yedekleme özelliği (bool)"""
    
    FEATURES_ENABLE_REPORTS = 'features.enable_reports'
    """Raporlar özelliği (bool)"""
    
    FEATURES_ENABLE_CHARTS = 'features.enable_charts'
    """Grafikler özelliği (bool)"""
    
    # ==================== USER PREFERENCES SECTION ====================
    
    USER_LAST_ACTIVE_LOJMAN_ID = 'user.last_active_lojman_id'
    """Son açık lojman ID (int)"""
    
    USER_LAST_ACTIVE_PANEL = 'user.last_active_panel'
    """Son açık panel (str): 'dashboard', 'lojman', vb."""
    
    USER_PREFERRED_LANGUAGE = 'user.preferred_language'
    """Tercih edilen dil (str): 'tr', 'en'"""
    
    # ==================== UI PREFERENCES SECTION ====================
    
    UI_PREF_WINDOW_STATE = 'ui_preferences.window_state'
    """Pencere durumu (str): 'normal', 'maximized', 'minimized'"""
    
    UI_PREF_WINDOW_WIDTH = 'ui_preferences.last_window_width'
    """Son pencere genişliği (int)"""
    
    UI_PREF_WINDOW_HEIGHT = 'ui_preferences.last_window_height'
    """Son pencere yüksekliği (int)"""
    
    UI_PREF_SIDEBAR_COLLAPSED = 'ui_preferences.sidebar_collapsed'
    """Sidebar kapalı mı (bool)"""
    
    # ==================== FINANCIAL SECTION ====================
    
    FINANCIAL_CURRENCY = 'financial.currency'
    """Para birimi (str): 'TRY', 'USD'"""
    
    FINANCIAL_DECIMAL_PLACES = 'financial.decimal_places'
    """Ondalık basamak sayısı (int)"""
    
    FINANCIAL_DEFAULT_ACCOUNT_ID = 'financial.default_account_id'
    """Varsayılan hesap ID (int)"""
    
    # ==================== REPORTS SECTION ====================
    
    REPORTS_DEFAULT_DATE_FORMAT = 'reports.default_date_format'
    """Rapor tarih formatı (str): 'DD.MM.YYYY'"""
    
    REPORTS_INCLUDE_ZERO_VALUES = 'reports.include_zero_values'
    """Sıfır değerleri raporlarda göster (bool)"""


class ConfigDefaults:
    """Configuration varsayılan değerleri
    
    Constant olarak tanımlanan varsayılan değerler.
    JSON veya env'de override edilebilir.
    """
    
    # App
    DEFAULT_APP_NAME = 'Aidat Plus'
    DEFAULT_APP_VERSION = '1.3'
    DEFAULT_APP_DEBUG = False
    DEFAULT_APP_ENV = 'production'
    
    # Database
    DEFAULT_DB_TYPE = 'sqlite'
    DEFAULT_DB_URL = 'sqlite:///aidat_plus.db'
    DEFAULT_DB_POOL_SIZE = 10
    DEFAULT_DB_POOL_RECYCLE = 3600
    DEFAULT_DB_ECHO = False
    
    # UI
    DEFAULT_UI_THEME = 'dark'
    DEFAULT_UI_WIDTH = 1400
    DEFAULT_UI_HEIGHT = 900
    DEFAULT_UI_FONT_SIZE = 11
    
    # Logging
    DEFAULT_LOG_LEVEL = 'INFO'
    DEFAULT_LOG_FILE = 'logs/app.log'
    DEFAULT_LOG_MAX_BYTES = 10485760  # 10 MB
    DEFAULT_LOG_BACKUP_COUNT = 5
    
    # Financial
    DEFAULT_CURRENCY = 'TRY'
    DEFAULT_DECIMAL_PLACES = 2


class EnvironmentTypes:
    """Environment tipleri"""
    
    DEVELOPMENT = 'development'
    """Geliştirme ortamı"""
    
    PRODUCTION = 'production'
    """Üretim ortamı"""
    
    TESTING = 'testing'
    """Test ortamı"""


class LogLevels:
    """Logging seviyeleri"""
    
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


class ThemeTypes:
    """Tema tipleri"""
    
    DARK = 'dark'
    LIGHT = 'light'
    AUTO = 'auto'


class PanelNames:
    """Panel adları"""
    
    DASHBOARD = 'dashboard'
    LOJMAN = 'lojman'
    AIDAT = 'aidat'
    SAKIN = 'sakin'
    FINANS = 'finans'
    RAPORLAR = 'raporlar'
    AYARLAR = 'ayarlar'
