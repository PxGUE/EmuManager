import unittest.mock as mock
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest

from emumanager.controllers.workers import (
    UpdateWorker, ScanWorker, ScrapeWorker, CoreDownloadWorker,
    EmulatorInstallWorker, StartupWorker, EmulatorUninstallWorker,
    LaunchWorker, EmulatorInstallConfig
)

def test_scan_worker_success():
    db_path = Path("/tmp/test.db")
    directory = "/games/snes"
    worker = ScanWorker(db_path, directory)

    with patch('backend.database.DatabaseManager') as MockDB,          patch('backend.scanner.ScannerManager') as MockScanner:

        mock_scanner_instance = MockScanner.return_value
        mock_scanner_instance.scan_and_register.return_value = 10

        worker.run()

        MockDB.assert_called_once_with(db_path)
        MockScanner.assert_called_once_with(MockDB.return_value)
        mock_scanner_instance.scan_and_register.assert_called_once()

        args, kwargs = mock_scanner_instance.scan_and_register.call_args
        assert args[0] == directory
        assert 'progress_callback' in kwargs
        assert 'status_callback' in kwargs
        assert 'is_active_check' in kwargs

        worker.finished.emit.assert_called_once_with(10)

def test_scan_worker_failure():
    db_path = Path("/tmp/test.db")
    directory = "/games/snes"
    worker = ScanWorker(db_path, directory)

    with patch('backend.database.DatabaseManager', side_effect=Exception("DB Error")):
        worker.run()
        worker.finished.emit.assert_called_once_with(0)

def test_scan_worker_stop():
    worker = ScanWorker(Path("/tmp/test.db"), "/games")
    assert worker._is_active is True
    worker.stop()
    assert worker._is_active is False

def test_scrape_worker_success():
    mock_scanner = MagicMock()
    mock_scanner.scrape_missing_metadata.return_value = 5
    worker = ScrapeWorker(mock_scanner)

    worker.run()

    mock_scanner.scrape_missing_metadata.assert_called_once()
    args, kwargs = mock_scanner.scrape_missing_metadata.call_args
    assert 'progress_callback' in kwargs
    assert 'status_callback' in kwargs

    # Test progress callback
    progress_cb = kwargs['progress_callback']
    progress_cb(0.5, "Downloading...")
    worker.progress.emit.assert_called_once_with(0.5)
    worker.status.emit.assert_called_once_with("Downloading...")

    worker.finished.emit.assert_called_once_with(5)

def test_scrape_worker_failure():
    mock_scanner = MagicMock()
    mock_scanner.scrape_missing_metadata.side_effect = Exception("Scrape Error")
    worker = ScrapeWorker(mock_scanner)

    worker.run()
    worker.finished.emit.assert_called_once_with(0)

def test_scrape_worker_stop():
    worker = ScrapeWorker(MagicMock())
    assert worker._is_active is True
    worker.stop()
    assert worker._is_active is False

def test_emulator_install_worker_success():
    config = EmulatorInstallConfig(
        emu_id="dolphin",
        system_id="gc",
        url="http://example.com/dolphin.zip",
        dest_dir="/emus/dolphin",
        executable="dolphin-emu"
    )
    worker = EmulatorInstallWorker(config)

    import mango_engine
    mango_engine.install_emulator_orchestra.return_value = "/emus/dolphin/dolphin-emu"

    worker.run()

    mango_engine.install_emulator_orchestra.assert_called_once()
    args, kwargs = mango_engine.install_emulator_orchestra.call_args
    assert args[0] == "dolphin"
    assert args[1] == "gc"
    assert args[2] == "http://example.com/dolphin.zip"

    worker.status.emit.assert_any_call("dolphin", "install_success")
    worker.finished.emit.assert_called_once_with("dolphin", "/emus/dolphin/dolphin-emu")

def test_emulator_install_worker_failure():
    config = EmulatorInstallConfig(
        emu_id="dolphin",
        system_id="gc",
        url="http://example.com/dolphin.zip",
        dest_dir="/emus/dolphin",
        executable="dolphin-emu"
    )
    worker = EmulatorInstallWorker(config)

    import mango_engine
    mango_engine.install_emulator_orchestra.return_value = None

    worker.run()

    worker.status.emit.assert_any_call("dolphin", "install_failed")
    worker.finished.emit.assert_called_once_with("dolphin", "")

def test_emulator_install_worker_exception():
    config = EmulatorInstallConfig("dolphin", "gc", "url", "dir", "exe")
    worker = EmulatorInstallWorker(config)

    import mango_engine
    mango_engine.install_emulator_orchestra.side_effect = Exception("OS Error")

    worker.run()

    # It should emit "install_error|OS Error"
    worker.status.emit.assert_any_call("dolphin", "install_error|OS Error")
    worker.finished.emit.assert_called_once_with("dolphin", "")

def test_startup_worker_success():
    mock_ctrl = MagicMock()
    mock_ctrl.precharge_ecosystem.return_value = {"total_games": 100}
    worker = StartupWorker(mock_ctrl)

    # Mock time.sleep to speed up tests
    with patch('time.sleep'):
        worker.run()

    mock_ctrl.proactive_background_load.assert_called_once()
    mock_ctrl.precharge_ecosystem.assert_called_once()

    # Check signals
    worker.status.emit.assert_any_call("startup_native")
    worker.status.emit.assert_any_call("startup_db")
    worker.status.emit.assert_any_call("startup_services")
    worker.status.emit.assert_any_call("startup_ready")

    worker.progress.emit.assert_any_call(0.10)
    worker.progress.emit.assert_any_call(0.90)
    worker.progress.emit.assert_any_call(1.0)

    worker.finished.emit.assert_called_once()

def test_startup_worker_exception():
    mock_ctrl = MagicMock()
    mock_ctrl.proactive_background_load.side_effect = Exception("Crash")
    worker = StartupWorker(mock_ctrl)

    with patch('time.sleep'):
        worker.run()

    # Should still emit finished even on error
    worker.finished.emit.assert_called_once()

def test_update_worker_dev_mode():
    worker = UpdateWorker(current_version="1.0.0")

    with patch('core.config.AppConfig.IS_DEV_MODE', True),          patch('time.sleep'):
        worker.run()

    worker.finished.emit.assert_called_once_with([])

def test_update_worker_prod_mode():
    targets = {"app": "1.0.0"}
    worker = UpdateWorker(current_version="1.0.0", targets=targets)

    import mango_engine
    mango_engine.check_all_updates.return_value = ["app_update"]

    with patch('core.config.AppConfig.IS_DEV_MODE', False):
        worker.run()

    mango_engine.check_all_updates.assert_called_once_with(targets)
    worker.finished.emit.assert_called_once_with(["app_update"])

def test_core_download_worker_success():
    mock_libretro = MagicMock()
    mock_libretro.download_core.return_value = "/path/to/core.so"
    worker = CoreDownloadWorker(mock_libretro, "snes9x")

    worker.run()

    mock_libretro.download_core.assert_called_once()
    worker.status.emit.assert_any_call("snes9x", "core_installed")
    worker.finished.emit.assert_called_once_with("snes9x", "/path/to/core.so")

def test_emulator_uninstall_worker_success():
    worker = EmulatorUninstallWorker("dolphin", "/emus/dolphin")

    import mango_engine
    worker.run()

    mango_engine.uninstall_emulator.assert_called_once_with("/emus/dolphin")
    worker.finished.emit.assert_called_once_with("dolphin", True)

def test_launch_worker_success():
    worker = LaunchWorker("runner", "game", "core")

    import mango_engine
    mango_engine.launch_game.return_value = 120

    worker.run()

    mango_engine.launch_game.assert_called_once_with("runner", "game", "core")
    worker.finished.emit.assert_called_once_with(120)
