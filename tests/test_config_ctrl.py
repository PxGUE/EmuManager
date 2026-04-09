import unittest.mock as mock
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest

from emumanager.controllers.config_ctrl import AppConfigController
from emumanager.core.config import AppConfig

@pytest.fixture(autouse=True)
def reset_app_config(mocker):
    """Resets AppConfig class variables before and after each test."""
    AppConfig._config_cache = None
    AppConfig._app_root = None
    # Mocking EmuLog to avoid actual logging during tests
    mocker.patch("emumanager.controllers.config_ctrl.EmuLog")
    yield
    AppConfig._config_cache = None
    AppConfig._app_root = None

@pytest.fixture
def temp_data_dir(tmp_path, mocker):
    """Mocks get_app_data_dir to return a temporary directory."""
    mock_dir = tmp_path / "app_data"
    mock_dir.mkdir()
    # Use patch.object on AppConfig directly to ensure it takes effect everywhere
    mocker.patch("emumanager.core.config.AppConfig.get_app_data_dir", return_value=mock_dir)
    # Also patch where it might be imported as AppConfig
    mocker.patch("emumanager.controllers.config_ctrl.AppConfig.get_app_data_dir", return_value=mock_dir)
    return mock_dir

@pytest.fixture
def controller(temp_data_dir):
    # Ensure a fresh state for each test
    AppConfig._config_cache = None
    return AppConfigController()

def test_initialization(controller):
    assert controller is not None

def test_get_language_default(controller):
    # Default should be "es" based on AppConfig
    assert controller.get_language() == "es"

def test_set_language_supported(controller):
    # Test changing to "en"
    controller.set_language("en")
    assert controller.get_language() == "en"
    controller.language_changed.emit.assert_called_once_with("en")

    # Test changing back to "es"
    controller.language_changed.emit.reset_mock()
    controller.set_language("es")
    assert controller.get_language() == "es"
    controller.language_changed.emit.assert_called_once_with("es")

def test_set_language_unsupported(controller):
    controller.language_changed.emit.reset_mock()

    # Ensure starting point
    assert controller.get_language() == "es"

    # Try unsupported language
    controller.set_language("fr")
    assert controller.get_language() == "es"
    controller.language_changed.emit.assert_not_called()

    # Try empty string
    controller.set_language("")
    assert controller.get_language() == "es"
    controller.language_changed.emit.assert_not_called()

def test_api_credentials_screenscraper(controller, mocker):
    # Test user
    controller.set_api_credential("screenscraper_user", "jules_user")
    assert controller.get_api_credential("screenscraper_user") == "jules_user"

    # Test pass (requires mocking CredentialsManager since AppConfig calls it)
    # Patch in core.config where it's imported inside the methods
    # Using 'emumanager.core.config.CredentialsManager' might not work because it's imported locally
    # Let's try patching 'core.security.CredentialsManager' and see if it works
    mock_cm = mocker.patch("core.security.CredentialsManager")

    mock_cm.get_user_password.return_value = "jules_pass"
    assert controller.get_api_credential("screenscraper_pass") == "jules_pass"
    mock_cm.get_user_password.assert_called_with("screenscraper", "jules_user")

    controller.set_api_credential("screenscraper_pass", "new_jules_pass")
    mock_cm.save_user_password.assert_called_with("screenscraper", "jules_user", "new_jules_pass")

def test_api_credentials_gametdb(controller):
    assert controller.get_api_credential("gametdb_mode") == "web"
    controller.set_api_credential("gametdb_mode", "local")
    assert controller.get_api_credential("gametdb_mode") == "local"

def test_api_credentials_discord_rpc(controller, mocker):
    # Check what AppConfig the controller is using
    import emumanager.controllers.config_ctrl as config_ctrl_module

    # Ensure a fresh start
    config_ctrl_module.AppConfig.set_discord_rpc_enabled(True)
    assert config_ctrl_module.AppConfig.get_discord_rpc_enabled() is True
    assert controller.get_api_credential("discord_rpc") == "true"

    # Trace the call on the actual module's AppConfig
    spy = mocker.spy(config_ctrl_module.AppConfig, "set_discord_rpc_enabled")

    controller.set_api_credential("discord_rpc", "false")

    spy.assert_called_once_with(False)
    assert config_ctrl_module.AppConfig.get_discord_rpc_enabled() is False
    assert controller.get_api_credential("discord_rpc") == "false"

    controller.set_api_credential("discord_rpc", "true")
    assert config_ctrl_module.AppConfig.get_discord_rpc_enabled() is True
    assert controller.get_api_credential("discord_rpc") == "true"

def test_api_credentials_unknown(controller):
    assert controller.get_api_credential("unknown_service") == ""
    # Setting unknown should not crash
    controller.set_api_credential("unknown_service", "value")

def test_select_roms_directory_success(controller, mocker):
    import emumanager.controllers.config_ctrl as config_ctrl_module
    mock_file_dialog = mocker.patch("emumanager.controllers.config_ctrl.QFileDialog")

    # Setup initial path
    config_ctrl_module.AppConfig.set_roms_path("/initial/roms")

    # Mock user selecting a new directory
    new_dir = "/new/roms/path"
    mock_file_dialog.getExistingDirectory.return_value = new_dir

    result = controller.select_roms_directory()

    assert result == new_dir
    assert config_ctrl_module.AppConfig.get_roms_path() == new_dir
    mock_file_dialog.getExistingDirectory.assert_called_once_with(
        None, "Seleccionar Carpeta de ROMs", "/initial/roms"
    )

def test_select_roms_directory_cancel(controller, mocker):
    import emumanager.controllers.config_ctrl as config_ctrl_module
    mock_file_dialog = mocker.patch("emumanager.controllers.config_ctrl.QFileDialog")

    # Setup initial path
    initial_path = "/initial/roms"
    config_ctrl_module.AppConfig.set_roms_path(initial_path)

    # Mock user cancelling (returns empty string or None in some Qt versions, but controller checks for truthy)
    mock_file_dialog.getExistingDirectory.return_value = ""

    result = controller.select_roms_directory()

    assert result == initial_path
    assert config_ctrl_module.AppConfig.get_roms_path() == initial_path

def test_select_cores_directory_success(controller, mocker, temp_data_dir):
    import emumanager.controllers.config_ctrl as config_ctrl_module
    mock_file_dialog = mocker.patch("emumanager.controllers.config_ctrl.QFileDialog")

    # Setup initial path within temp_data_dir
    initial_path = str(temp_data_dir / "initial_emus")
    config_ctrl_module.AppConfig.set_emulators_path(initial_path)

    # Mock user selecting a new directory
    new_dir = str(temp_data_dir / "new_emus_path")
    mock_file_dialog.getExistingDirectory.return_value = new_dir

    result = controller.select_cores_directory()

    assert result == new_dir
    assert config_ctrl_module.AppConfig.get_emulators_path() == new_dir
    mock_file_dialog.getExistingDirectory.assert_called_once_with(
        None, "Seleccionar Directorio Principal para Emuladores", initial_path
    )

def test_select_cores_directory_cancel(controller, mocker, temp_data_dir):
    import emumanager.controllers.config_ctrl as config_ctrl_module
    mock_file_dialog = mocker.patch("emumanager.controllers.config_ctrl.QFileDialog")

    # Setup initial path within temp_data_dir
    initial_path = str(temp_data_dir / "initial_emus")
    config_ctrl_module.AppConfig.set_emulators_path(initial_path)

    # Mock user cancelling
    mock_file_dialog.getExistingDirectory.return_value = ""

    result = controller.select_cores_directory()

    assert result == initial_path
    assert config_ctrl_module.AppConfig.get_emulators_path() == initial_path
