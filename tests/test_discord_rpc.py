import sys
from unittest.mock import MagicMock

# Mock heavy/problematic dependencies
sys.modules["psutil"] = MagicMock()
sys.modules["PySide6"] = MagicMock()
sys.modules["PySide6.QtWidgets"] = MagicMock()
sys.modules["PySide6.QtCore"] = MagicMock()
sys.modules["PySide6.QtQml"] = MagicMock()

import pytest
from unittest.mock import MagicMock, patch
import os

from emumanager.backend.discord_rpc import DiscordRPCManager

@pytest.fixture
def mock_pypresence(monkeypatch):
    mock_presence_class = MagicMock()
    mock_presence_instance = mock_presence_class.return_value
    # Mock at the level of the module that imports it
    monkeypatch.setattr("emumanager.backend.discord_rpc.PYPRESENCE_AVAILABLE", True)
    # We need to ensure 'Presence' exists in the module namespace for monkeypatch to work
    import emumanager.backend.discord_rpc as drpc
    drpc.Presence = mock_presence_class
    return mock_presence_class, mock_presence_instance

@pytest.fixture
def mock_logger(monkeypatch):
    mock_log = MagicMock()
    monkeypatch.setattr("emumanager.backend.discord_rpc.EmuLog", mock_log)
    return mock_log

def test_initialization():
    manager = DiscordRPCManager()
    assert manager.rpc is None
    assert manager._is_connected is False
    assert manager._enabled is False

def test_set_enabled(mock_logger):
    manager = DiscordRPCManager()
    with patch.object(manager, 'clear_presence') as mock_clear:
        manager.set_enabled(True)
        assert manager._enabled is True
        mock_clear.assert_not_called()

        manager.set_enabled(False)
        assert manager._enabled is False
        mock_clear.assert_called_once()

def test_connect_pypresence_unavailable(monkeypatch):
    monkeypatch.setattr("emumanager.backend.discord_rpc.PYPRESENCE_AVAILABLE", False)
    manager = DiscordRPCManager()
    manager.set_enabled(True)
    assert manager.connect() is False
    assert manager._is_connected is False

def test_connect_disabled():
    manager = DiscordRPCManager()
    manager.set_enabled(False)
    assert manager.connect() is False
    assert manager._is_connected is False

def test_connect_success(mock_pypresence, mock_logger):
    mock_class, mock_instance = mock_pypresence
    manager = DiscordRPCManager()
    manager.set_enabled(True)

    from emumanager.core.config import AppConfig
    expected_id = AppConfig.get_discord_client_id()

    assert manager.connect() is True
    assert manager._is_connected is True
    mock_class.assert_called_with(expected_id)
    mock_instance.connect.assert_called_once()

def test_connect_custom_id_env(mock_pypresence, mock_logger, monkeypatch):
    custom_id = "987654321"
    monkeypatch.setenv("DISCORD_CLIENT_ID", custom_id)

    mock_class, mock_instance = mock_pypresence
    manager = DiscordRPCManager()
    manager.set_enabled(True)

    assert manager.connect() is True
    mock_class.assert_called_with(custom_id)

def test_connect_already_connected(mock_pypresence):
    mock_class, mock_instance = mock_pypresence
    manager = DiscordRPCManager()
    manager.set_enabled(True)
    manager._is_connected = True

    assert manager.connect() is True
    # If already connected, we don't call Presence() again
    # Since we set _is_connected=True manually, it skips connect logic
    # But in success case before it might have been called.
    # To be sure, we check it's NOT called again in this test specifically.
    mock_class.reset_mock()
    assert manager.connect() is True
    mock_class.assert_not_called()

def test_connect_exception(mock_pypresence, mock_logger):
    mock_class, mock_instance = mock_pypresence
    mock_instance.connect.side_effect = Exception("Connection error")
    manager = DiscordRPCManager()
    manager.set_enabled(True)

    assert manager.connect() is False
    assert manager._is_connected is False
    mock_logger.debug.assert_called()

def test_update_presence_success(mock_pypresence, mock_logger):
    mock_class, mock_instance = mock_pypresence
    manager = DiscordRPCManager()
    manager.set_enabled(True)

    with patch('time.time', return_value=12345.67):
        manager.update_presence("Super Mario", "GBA")

    assert manager._is_connected is True
    mock_instance.update.assert_called_with(
        state="En GBA",
        details="Super Mario",
        start=12345.67,
        large_image="gba",
        large_text="EmuManager",
        small_image="logo",
        small_text="Viviendo la nostalgia"
    )
    mock_logger.info.assert_called()

def test_update_presence_no_platform(mock_pypresence, mock_logger):
    mock_class, mock_instance = mock_pypresence
    manager = DiscordRPCManager()
    manager.set_enabled(True)

    with patch('time.time', return_value=12345.67):
        manager.update_presence("Tetris", None)

    mock_instance.update.assert_called_with(
        state="Jugando",
        details="Tetris",
        start=12345.67,
        large_image="logo",
        large_text="EmuManager",
        small_image="logo",
        small_text="Viviendo la nostalgia"
    )

def test_update_presence_exception(mock_pypresence, mock_logger):
    mock_class, mock_instance = mock_pypresence
    manager = DiscordRPCManager()
    manager.set_enabled(True)
    manager._is_connected = True
    manager.rpc = mock_instance

    mock_instance.update.side_effect = Exception("Update error")
    manager.update_presence("Game", "Platform")

    assert manager._is_connected is False
    mock_logger.error.assert_called()

def test_clear_presence_success(mock_pypresence, mock_logger):
    mock_class, mock_instance = mock_pypresence
    manager = DiscordRPCManager()
    manager.rpc = mock_instance
    manager._is_connected = True

    manager.clear_presence()
    mock_instance.clear.assert_called_once()
    mock_logger.info.assert_called_with("Discord RPC: Estado limpiado.")

def test_disconnect(mock_pypresence, mock_logger):
    mock_class, mock_instance = mock_pypresence
    manager = DiscordRPCManager()
    manager.rpc = mock_instance
    manager._is_connected = True

    manager.disconnect()
    mock_instance.close.assert_called_once()
    assert manager._is_connected is False
    assert manager.rpc is None
    mock_logger.info.assert_called_with("Discord RPC: Desconectado.")
