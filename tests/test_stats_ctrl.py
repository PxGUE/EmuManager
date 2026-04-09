import sys
import os
from unittest.mock import MagicMock, patch
import platform as py_platform
import pytest

# Add emumanager to sys.path BEFORE any project imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'emumanager')))

# We must mock modules globally because imports like StatsController happen
# at test collection time, and fixture `autouse` is too late.
# We will save the original modules and restore them.
_original_modules = sys.modules.copy()

sys.modules['psutil'] = MagicMock()
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['pypresence'] = MagicMock()

# Mock the signals and slots for QObject since we mocked PySide6
class MockQObject:
    def __init__(self, parent=None, **kwargs):
        pass

sys.modules['PySide6.QtCore'].QObject = MockQObject
sys.modules['PySide6.QtCore'].Slot = lambda *args, **kwargs: lambda f: f
sys.modules['PySide6.QtCore'].Signal = MagicMock

from controllers.stats_ctrl import StatsController
from core.config import AppConfig

def teardown_module(module):
    """Restore original sys.modules to prevent test pollution."""
    # Remove mock modules that weren't in the original
    for mod in list(sys.modules.keys()):
        if mod not in _original_modules:
            del sys.modules[mod]
    # Restore original modules
    sys.modules.update(_original_modules)

@pytest.fixture
def stats_controller():
    mock_db = MagicMock()
    return StatsController(db=mock_db)

def test_get_system_info_import_error(stats_controller):
    original_import = __import__
    def mock_import(name, *args, **kwargs):
        if name == 'mango_engine':
            raise ImportError("No module named 'mango_engine'")
        return original_import(name, *args, **kwargs)

    with patch('builtins.__import__', side_effect=mock_import):
        info = stats_controller.get_system_info()

    assert info['is_engine_ready'] is False
    assert info['mango_version'] == "N/A"
    assert info['app_name'] == AppConfig.APP_NAME
    assert info['app_version'] == AppConfig.APP_VERSION
    assert "os" in info

def test_get_system_info_success(stats_controller):
    mock_mango_engine = MagicMock()

    original_import = __import__
    def mock_import(name, *args, **kwargs):
        if name == 'mango_engine':
            return mock_mango_engine
        return original_import(name, *args, **kwargs)

    with patch('builtins.__import__', side_effect=mock_import):
        info = stats_controller.get_system_info()

    assert info['is_engine_ready'] is True
    assert info['mango_version'] == AppConfig.MANGO_VERSION
    assert info['app_name'] == AppConfig.APP_NAME
    assert info['app_version'] == AppConfig.APP_VERSION
    assert "os" in info
