import unittest.mock as mock
from unittest.mock import MagicMock, patch
import pytest

from emumanager.backend.scanner import ScannerManager

def test_scanner_manager_init():
    db_mock = MagicMock()
    scanner = ScannerManager(db_mock)
    assert scanner.db == db_mock
    assert "zip" in scanner.SUPPORTED_EXTENSIONS

@patch("emumanager.backend.scanner.mango_engine", None)
@patch("emumanager.backend.scanner.EmuLog")
def test_scan_and_register_no_mango(mock_log):
    db_mock = MagicMock()
    scanner = ScannerManager(db_mock)
    result = scanner.scan_and_register("/some/path")
    assert result == 0
    mock_log.error.assert_called_with("Entorno no preparado para escaneo nativo.")

@patch("emumanager.backend.scanner.mango_engine")
@patch("emumanager.backend.scanner.EmuLog")
def test_scan_and_register_success(mock_log, mock_mango):
    db_mock = MagicMock()
    db_mock.db_path = "/path/to/db"
    mock_mango.scan_directory_to_db.return_value = 5

    scanner = ScannerManager(db_mock)
    result = scanner.scan_and_register("/roms", progress_callback=lambda x: None)

    assert result == 5
    mock_mango.scan_directory_to_db.assert_called_once()
    mock_log.info.assert_called()

@patch("emumanager.backend.scanner.mango_engine")
@patch("emumanager.backend.scanner.EmuLog")
def test_scan_and_register_exception(mock_log, mock_mango):
    db_mock = MagicMock()
    db_mock.db_path = "/path/to/db"
    mock_mango.scan_directory_to_db.side_effect = Exception("Mango error")

    scanner = ScannerManager(db_mock)
    result = scanner.scan_and_register("/roms")

    assert result == 0
    mock_log.error.assert_called()

@patch("emumanager.backend.scanner.mango_engine", None)
@patch("emumanager.backend.scanner.EmuLog")
def test_scrape_missing_metadata_no_mango(mock_log):
    db_mock = MagicMock()
    scanner = ScannerManager(db_mock)
    result = scanner.scrape_missing_metadata()
    assert result == 0
    mock_log.error.assert_called_with("El motor M.A.N.G.O. no está disponible para el scraping.")

@patch("emumanager.backend.scanner.mango_engine")
@patch("emumanager.backend.scanner.AppConfig")
@patch("emumanager.backend.scanner.EmuLog")
def test_scrape_missing_metadata_no_roms_path(mock_log, mock_config, mock_mango):
    mock_config.get_roms_path.return_value = ""
    db_mock = MagicMock()
    scanner = ScannerManager(db_mock)
    result = scanner.scrape_missing_metadata()
    assert result == 0

@patch("emumanager.backend.scanner.mango_engine")
@patch("emumanager.backend.scanner.AppConfig")
@patch("emumanager.backend.scanner.EmuLog")
def test_scrape_missing_metadata_success(mock_log, mock_config, mock_mango):
    mock_config.get_roms_path.return_value = "/roms"
    mock_config.get_screenscraper_user.return_value = "user"
    mock_config.get_screenscraper_pass.return_value = "pass"
    mock_config.get_database_path.return_value = "/db"
    mock_config.get_gametdb_mode.return_value = "web"

    mock_mango.start_batch_scrape.return_value = 10

    status_cb = MagicMock()
    db_mock = MagicMock()
    scanner = ScannerManager(db_mock)
    result = scanner.scrape_missing_metadata(status_callback=status_cb)

    assert result == 10
    status_cb.assert_any_call("scrape_starting")
    status_cb.assert_any_call("scrape_finished")
    mock_mango.start_batch_scrape.assert_called_once()

@patch("emumanager.backend.scanner.mango_engine")
@patch("emumanager.backend.scanner.AppConfig")
@patch("emumanager.backend.scanner.EmuLog")
def test_scrape_missing_metadata_exception(mock_log, mock_config, mock_mango):
    mock_config.get_roms_path.return_value = "/roms"
    mock_config.get_screenscraper_user.return_value = "user"
    mock_config.get_screenscraper_pass.return_value = "pass"
    mock_config.get_database_path.return_value = "/db"

    mock_mango.start_batch_scrape.side_effect = Exception("Scrape error")

    db_mock = MagicMock()
    scanner = ScannerManager(db_mock)
    result = scanner.scrape_missing_metadata()

    assert result == 0
    mock_log.error.assert_called()
