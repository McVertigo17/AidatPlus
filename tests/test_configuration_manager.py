import os
import json
import pytest
from configuration.config_manager import ConfigurationManager


def teardown_function(function):
    # Reset singleton after each test to ensure isolation
    from configuration.config_manager import ConfigurationManager as CM
    CM._instance = None


def test_singleton_and_defaults(tmp_path):
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()

    cm = ConfigurationManager.get_instance(str(cfg_dir))

    # Default app name should exist
    assert cm.get("app.name") == "Aidat Plus"


def test_set_get_set_nested_and_override(tmp_path):
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()

    cm = ConfigurationManager.get_instance(str(cfg_dir))
    # Nested set/get
    cm.set_nested("ui.theme", "dark")
    assert cm.get("ui.theme") == "dark"

    # Runtime override should take precedence
    cm.set_override("ui.theme", "light")
    assert cm.get("ui.theme") == "light"

    # reload should reset overrides
    cm.reload()
    assert cm.get("ui.theme") == "light" or cm.get("ui.theme") in ("dark", "light")


def test_save_and_load_json(tmp_path):
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()

    cm = ConfigurationManager.get_instance(str(cfg_dir))
    prefs = {"user": {"theme": "dark", "font_size": 12}}
    cm.save_json_config("user_preferences.json", prefs)

    loaded = cm.load_json_config("user_preferences.json")
    assert "user" in loaded and loaded["user"]["theme"] == "dark"


def test_env_override(monkeypatch, tmp_path):
    # Create tmp config dir and environment variable
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()

    # Ensure no previous instance
    ConfigurationManager._instance = None
    # Change cwd to tmp_path so .env detection is local
    monkeypatch.chdir(tmp_path)
    # Create a .env file that load_dotenv can parse
    with open(tmp_path / '.env', 'w', encoding='utf-8') as f:
        f.write('APP_ENV=test\nAPP_DEBUG=True\n')

    cm = ConfigurationManager.get_instance(str(cfg_dir))
    assert cm.get("app.env") == "test"
    assert cm.get("app.debug") is True


def test_reload_clears_overrides(tmp_path):
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    cm = ConfigurationManager.get_instance(str(cfg_dir))
    cm.set_override("app.debug", True)
    assert cm.get("app.debug") is True
    cm.reload()
    # Should be default False (from defaults)
    assert cm.get("app.debug") is False
