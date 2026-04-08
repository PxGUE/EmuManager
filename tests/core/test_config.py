import pytest
import os
import json
import sys
from pathlib import Path
from core.config import AppConfig

@pytest.fixture(autouse=True)
def reset_app_config():
    """Resets AppConfig class variables before and after each test."""
    AppConfig._config_cache = None
    AppConfig._app_root = None
    yield
    AppConfig._config_cache = None
    AppConfig._app_root = None

@pytest.fixture
def temp_data_dir(tmp_path, mocker):
    """Mocks get_app_data_dir to return a temporary directory."""
    mock_dir = tmp_path / "app_data"
    mock_dir.mkdir()
    mocker.patch.object(AppConfig, 'get_app_data_dir', return_value=mock_dir)
    return mock_dir

def test_set_app_root():
    root = Path("/fake/root")
    AppConfig.set_app_root(root)
    assert AppConfig._app_root == root

def test_get_asset_path_with_root():
    root = Path("/fake/root")
    AppConfig.set_app_root(root)
    asset_path = AppConfig.get_asset_path("assets", "icon.png")
    assert asset_path == root / "assets" / "icon.png"

def test_get_asset_path_without_root():
    # It should fallback to a path relative to config.py
    asset_path = AppConfig.get_asset_path("assets", "icon.png")
    assert "assets" in asset_path.parts
    assert "icon.png" in asset_path.parts
    assert asset_path.is_absolute()

def test_get_app_data_dir_dev_mode(mocker):
    # Mocking sys.frozen and APPIMAGE to be False
    mocker.patch.object(sys, 'frozen', False, create=True)
    mocker.patch.dict(os.environ, {}, clear=True)
    # Mock mkdir to avoid creating directories in the repo
    mocker.patch.object(Path, 'mkdir')

    # Path to config.py is emumanager/core/config.py
    # project_root should be parent.parent.parent
    data_dir = AppConfig.get_app_data_dir()
    assert data_dir.name == "data"
    # We can't easily assert exists() if we mocked mkdir,
    # but we can verify it was called
    Path.mkdir.assert_called()

def test_config_persistence(temp_data_dir):
    assert AppConfig.get_roms_path() == ""
    AppConfig.set_roms_path("/path/to/roms")
    assert AppConfig.get_roms_path() == "/path/to/roms"

    # Verify it was saved to file
    config_file = temp_data_dir / "config.json"
    assert config_file.exists()
    with open(config_file, 'r') as f:
        data = json.load(f)
    assert data["roms_path"] == "/path/to/roms"

def test_emulators_path_default(temp_data_dir):
    expected_default = str(temp_data_dir / "emulators")
    emu_path = AppConfig.get_emulators_path()
    assert emu_path == expected_default
    assert Path(emu_path).exists()

def test_emulators_path_custom(temp_data_dir):
    custom_path = str(temp_data_dir / "custom_emus")
    AppConfig.set_emulators_path(custom_path)
    assert AppConfig.get_emulators_path() == custom_path
    assert Path(custom_path).exists()

def test_screenscraper_credentials(mocker, temp_data_dir):
    # Mock CredentialsManager
    from core.security import CredentialsManager
    mock_cm = mocker.patch('core.security.CredentialsManager')
    mock_cm.get_user_password.return_value = "secret_pass"

    AppConfig.set_screenscraper_user("test_user")
    assert AppConfig.get_screenscraper_user() == "test_user"

    # Test getting password
    pwd = AppConfig.get_screenscraper_pass()
    assert pwd == "secret_pass"
    mock_cm.get_user_password.assert_called_with("screenscraper", "test_user")

    # Test setting password
    AppConfig.set_screenscraper_pass("new_pass")
    mock_cm.save_user_password.assert_called_with("screenscraper", "test_user", "new_pass")

def test_language_settings(temp_data_dir):
    assert AppConfig.get_language() == "es" # Default
    AppConfig.set_language("en")
    assert AppConfig.get_language() == "en"

def test_database_path(temp_data_dir):
    db_path = AppConfig.get_database_path()
    assert db_path == temp_data_dir / "db" / "emumanager.db"

def test_media_dir_creation(temp_data_dir):
    media_dir = AppConfig.get_media_dir("gba", "covers")
    assert media_dir == temp_data_dir / "media" / "gba" / "covers"
    assert media_dir.exists()

def test_discord_rpc_enabled(temp_data_dir):
    assert AppConfig.get_discord_rpc_enabled() is True # Default
    AppConfig.set_discord_rpc_enabled(False)
    assert AppConfig.get_discord_rpc_enabled() is False
