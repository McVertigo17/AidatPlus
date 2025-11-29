"""Configuration Package

Aidat Plus uygulaması için merkezi konfigürasyon yönetimi.

Module exports:
    - ConfigurationManager: Merkezi konfigürasyon yöneticisi (Singleton)
    - ConfigKeys: Configuration anahtarları (constants)
    - ConfigDefaults: Varsayılan değerler
    - EnvironmentTypes: Environment tipleri
    - LogLevels: Logging seviyeleri
    - ThemeTypes: Tema tipleri
    - PanelNames: Panel adları

Example:
    >>> from configuration import ConfigurationManager, ConfigKeys
    >>> config = ConfigurationManager.get_instance()
    >>> db_url = config.get(ConfigKeys.DATABASE_URL)
    >>> theme = config.get(ConfigKeys.UI_THEME, 'dark')
"""

from configuration.config_manager import ConfigurationManager
from configuration.constants import (
    ConfigKeys,
    ConfigDefaults,
    EnvironmentTypes,
    LogLevels,
    ThemeTypes,
    PanelNames
)

__all__ = [
    'ConfigurationManager',
    'ConfigKeys',
    'ConfigDefaults',
    'EnvironmentTypes',
    'LogLevels',
    'ThemeTypes',
    'PanelNames'
]

__version__ = '1.0'
__author__ = 'Aidat Plus Development Team'
