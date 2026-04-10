import unittest.mock as mock
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest

from emumanager.backend.libretro import LibretroManager

@pytest.fixture
def libretro_manager(tmp_path):
    return LibretroManager(emus_base_path=tmp_path)

def test_get_core_for_platform_valid(libretro_manager):
    # Tests happy path for known platforms
    assert libretro_manager.get_core_for_platform("snes") == "snes9x"
    assert libretro_manager.get_core_for_platform("gba") == "mgba"
    assert libretro_manager.get_core_for_platform("gc") == "dolphin"

def test_get_core_for_platform_case_insensitivity(libretro_manager):
    # Tests case insensitivity
    assert libretro_manager.get_core_for_platform("SNES") == "snes9x"
    assert libretro_manager.get_core_for_platform("Snes") == "snes9x"
    assert libretro_manager.get_core_for_platform("Gba") == "mgba"

def test_get_core_for_platform_unsupported(libretro_manager):
    # Tests unsupported platforms
    assert libretro_manager.get_core_for_platform("unsupported_platform") is None
    assert libretro_manager.get_core_for_platform("xbox") is None

def test_get_core_for_platform_empty_string(libretro_manager):
    # Tests empty string input
    assert libretro_manager.get_core_for_platform("") is None

def test_download_core_mango_missing(libretro_manager):
    # Tests download_core returns None if mango_engine is missing
    with patch("emumanager.backend.libretro.mango_engine", None):
        assert libretro_manager.download_core("snes9x") is None

def test_download_core_success_clean_id(libretro_manager, tmp_path):
    # Tests successful core download with a clean ID
    mock_mango = MagicMock()
    mock_mango.download_core.return_value = "snes9x_libretro.so"

    with patch("emumanager.backend.libretro.mango_engine", mock_mango), \
         patch("emumanager.backend.libretro.EmuLog") as mock_log:

        result = libretro_manager.download_core("snes9x")

        assert result == "snes9x_libretro.so"
        # Verify directory creation: cores/snes
        expected_dir = tmp_path / "cores" / "snes"
        assert expected_dir.is_dir()

        # Verify mango_engine call
        mock_mango.download_core.assert_called_once_with(
            "snes9x", str(expected_dir), None, None
        )

        # Verify logging
        mock_log.info.assert_any_call(f"M.A.N.G.O: Instalando core snes9x en {expected_dir}")

def test_download_core_success_suffixed_id(libretro_manager, tmp_path):
    # Tests successful core download with a suffixed ID (_libretro)
    mock_mango = MagicMock()
    mock_mango.download_core.return_value = "mgba_libretro.so"

    with patch("emumanager.backend.libretro.mango_engine", mock_mango), \
         patch("emumanager.backend.libretro.EmuLog") as mock_log:

        result = libretro_manager.download_core("mgba_libretro")

        assert result == "mgba_libretro.so"
        # Verify directory creation: cores/gba
        expected_dir = tmp_path / "cores" / "gba"
        assert expected_dir.is_dir()

        # Verify mango_engine call
        mock_mango.download_core.assert_called_once_with(
            "mgba_libretro", str(expected_dir), None, None
        )

def test_download_core_with_callbacks(libretro_manager, tmp_path):
    # Tests that callbacks are correctly passed to mango_engine
    mock_mango = MagicMock()
    prog_cb = MagicMock()
    stat_cb = MagicMock()

    with patch("emumanager.backend.libretro.mango_engine", mock_mango):
        libretro_manager.download_core("snes9x", progress_callback=prog_cb, status_callback=stat_cb)

        expected_dir = tmp_path / "cores" / "snes"
        mock_mango.download_core.assert_called_once_with(
            "snes9x", str(expected_dir), prog_cb, stat_cb
        )

def test_download_core_exception(libretro_manager, tmp_path):
    # Tests that exceptions in mango_engine are caught and return None
    mock_mango = MagicMock()
    mock_mango.download_core.side_effect = Exception("Download failed")

    with patch("emumanager.backend.libretro.mango_engine", mock_mango), \
         patch("emumanager.backend.libretro.EmuLog") as mock_log:

        result = libretro_manager.download_core("snes9x")

        assert result is None
        mock_log.error.assert_any_call("Error downloading core snes9x: Download failed")

def test_uninstall_core_not_found(libretro_manager):
    # Tests uninstallation when file does not exist
    result = libretro_manager.uninstall_core("non_existent_core")
    assert result is False

def test_uninstall_core_windows(libretro_manager, tmp_path):
    # Tests that .dll extension is used on Windows
    core_name = "snes9x"
    platform_id = "snes"

    with patch("platform.system", return_value="Windows"), \
         patch("emumanager.backend.libretro.EmuLog") as mock_log:
        core_dir = tmp_path / "cores" / platform_id
        core_dir.mkdir(parents=True, exist_ok=True)
        core_file = core_dir / f"{core_name}.dll"
        core_file.write_text("dummy")

        result = libretro_manager.uninstall_core(core_name)

        assert result is True
        assert not core_file.exists()
        mock_log.info.assert_called_with(f"Core eliminado del disco: {core_name}.dll")

def test_uninstall_core_linux(libretro_manager, tmp_path):
    # Tests that .so extension is used on Linux
    core_name = "snes9x"
    platform_id = "snes"

    with patch("platform.system", return_value="Linux"), \
         patch("emumanager.backend.libretro.EmuLog") as mock_log:
        core_dir = tmp_path / "cores" / platform_id
        core_dir.mkdir(parents=True, exist_ok=True)
        core_file = core_dir / f"{core_name}.so"
        core_file.write_text("dummy")

        result = libretro_manager.uninstall_core(core_name)

        assert result is True
        assert not core_file.exists()
        mock_log.info.assert_called_with(f"Core eliminado del disco: {core_name}.so")

def test_uninstall_core_exception(libretro_manager, tmp_path):
    # Tests that exceptions are caught and logged
    core_name = "snes9x"

    # We'll mock Path.exists to return True but Path.unlink to raise an exception
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.unlink", side_effect=Exception("Permission denied")), \
         patch("emumanager.backend.libretro.EmuLog") as mock_log:

        result = libretro_manager.uninstall_core(core_name)

        assert result is False
        mock_log.error.assert_called_with(f"Error al eliminar core {core_name}: Permission denied")
