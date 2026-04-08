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
