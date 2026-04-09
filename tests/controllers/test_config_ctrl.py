import sys
import os
from unittest.mock import MagicMock, patch

# Define functional mocks for PySide6
class MockQObject:
    def __init__(self, parent=None):
        pass

def MockSlot(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

class MockSignal:
    def __init__(self, *args, **kwargs):
        pass
    def emit(self, *args, **kwargs):
        pass

# Mock PySide6 BEFORE importing the controller
mock_pyside6 = MagicMock()
mock_pyside6_core = MagicMock()
mock_pyside6_widgets = MagicMock()

mock_pyside6_core.QObject = MockQObject
mock_pyside6_core.Slot = MockSlot
mock_pyside6_core.Signal = MockSignal

sys.modules['PySide6'] = mock_pyside6
sys.modules['PySide6.QtCore'] = mock_pyside6_core
sys.modules['PySide6.QtWidgets'] = mock_pyside6_widgets

import pytest

# Add emumanager to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../emumanager')))

# Mock core.logger and core.config before importing the controller
sys.modules['core.logger'] = MagicMock()
# We want to patch AppConfig later, but it's imported in config_ctrl.py
# If we mock it in sys.modules, we might have issues with how it's used.
# Let's try mocking it in sys.modules first.
mock_app_config = MagicMock()
sys.modules['core.config'] = MagicMock()
sys.modules['core.config'].AppConfig = mock_app_config

from controllers.config_ctrl import AppConfigController

@pytest.fixture
def config_ctrl():
    return AppConfigController()

def test_get_api_credential_screenscraper_user(config_ctrl):
    mock_app_config.get_screenscraper_user.return_value = "test_user"
    assert config_ctrl.get_api_credential("screenscraper_user") == "test_user"

def test_get_api_credential_screenscraper_pass(config_ctrl):
    mock_app_config.get_screenscraper_pass.return_value = "test_pass"
    assert config_ctrl.get_api_credential("screenscraper_pass") == "test_pass"

def test_get_api_credential_gametdb_mode(config_ctrl):
    mock_app_config.get_gametdb_mode.return_value = "web"
    assert config_ctrl.get_api_credential("gametdb_mode") == "web"

def test_get_api_credential_discord_rpc_true(config_ctrl):
    mock_app_config.get_discord_rpc_enabled.return_value = True
    assert config_ctrl.get_api_credential("discord_rpc") == "true"

def test_get_api_credential_discord_rpc_false(config_ctrl):
    mock_app_config.get_discord_rpc_enabled.return_value = False
    assert config_ctrl.get_api_credential("discord_rpc") == "false"

def test_get_api_credential_unrecognized(config_ctrl):
    assert config_ctrl.get_api_credential("unknown_service") == ""
    assert config_ctrl.get_api_credential("") == ""
    assert config_ctrl.get_api_credential("random") == ""
