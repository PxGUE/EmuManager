import sys
import os
from unittest.mock import MagicMock
from pathlib import Path

# Mock psutil, PySide6, and pypresence before they are imported
sys.modules['psutil'] = MagicMock()
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['pypresence'] = MagicMock()

import pytest

# Add emumanager to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

def test_uninstall_core_success_linux(libretro_manager, monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")

    # We need to test on a known platform, e.g., snes
    core_name = "snes9x"
    platform_id = "snes"

    # Create the dummy directory and file
    core_dir = libretro_manager.cores_path / platform_id
    core_dir.mkdir(parents=True, exist_ok=True)
    target_file = core_dir / f"{core_name}.so"
    target_file.touch()

    assert target_file.exists()

    result = libretro_manager.uninstall_core(core_name)

    assert result is True
    assert not target_file.exists()

def test_uninstall_core_success_windows(libretro_manager, monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")

    core_name = "snes9x"
    platform_id = "snes"

    # Create the dummy directory and file
    core_dir = libretro_manager.cores_path / platform_id
    core_dir.mkdir(parents=True, exist_ok=True)
    target_file = core_dir / f"{core_name}.dll"
    target_file.touch()

    assert target_file.exists()

    result = libretro_manager.uninstall_core(core_name)

    assert result is True
    assert not target_file.exists()

def test_uninstall_core_not_found(libretro_manager, monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")

    core_name = "snes9x"
    # Do not create the file

    result = libretro_manager.uninstall_core(core_name)

    assert result is False

def test_uninstall_core_exception(libretro_manager, monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")

    core_name = "snes9x"
    platform_id = "snes"

    core_dir = libretro_manager.cores_path / platform_id
    core_dir.mkdir(parents=True, exist_ok=True)
    target_file = core_dir / f"{core_name}.so"
    target_file.touch()

    # Mock unlink to raise an exception
    def mock_unlink(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "unlink", mock_unlink)

    result = libretro_manager.uninstall_core(core_name)

    assert result is False
    assert target_file.exists()  # File should still exist because unlink failed
