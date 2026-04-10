import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from emumanager.controllers.orch_ctrl import OrchestraController

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_libretro():
    return MagicMock()

@pytest.fixture
def orch_ctrl(mock_db, mock_libretro):
    with patch("emumanager.controllers.orch_ctrl.DiscordRPCManager"):
        return OrchestraController(mock_db, mock_libretro)

def test_find_emulator_executable_root(orch_ctrl, tmp_path):
    emu_id = "retroarch"
    emu_path = tmp_path / "emus"
    emu_path.mkdir()
    retro_dir = emu_path / emu_id
    retro_dir.mkdir()

    # We need to mock platform to know which exe name to use
    with patch("emumanager.controllers.orch_ctrl.py_platform.system", return_value="Linux"):
        exe_name = "RetroArch.AppImage"
        exe_file = retro_dir / exe_name
        exe_file.touch()

        with patch("emumanager.controllers.orch_ctrl.AppConfig.get_emulators_path", return_value=str(emu_path)):
            result = orch_ctrl._find_emulator_executable(emu_id)
            assert result == exe_file

def test_find_emulator_executable_subfolder(orch_ctrl, tmp_path):
    emu_id = "dolphin"
    emu_path = tmp_path / "emus"
    emu_path.mkdir()
    dolphin_dir = emu_path / emu_id
    dolphin_dir.mkdir()
    bin_dir = dolphin_dir / "bin"
    bin_dir.mkdir()

    with patch("emumanager.controllers.orch_ctrl.py_platform.system", return_value="Linux"):
        exe_name = "Dolphin.AppImage"
        exe_file = bin_dir / exe_name
        exe_file.touch()

        with patch("emumanager.controllers.orch_ctrl.AppConfig.get_emulators_path", return_value=str(emu_path)):
            result = orch_ctrl._find_emulator_executable(emu_id)
            assert result == exe_file

def test_find_emulator_executable_not_found(orch_ctrl, tmp_path):
    emu_id = "pcsx2"
    emu_path = tmp_path / "emus"
    emu_path.mkdir()
    pcsx2_dir = emu_path / emu_id
    pcsx2_dir.mkdir()

    with patch("emumanager.controllers.orch_ctrl.py_platform.system", return_value="Linux"):
        with patch("emumanager.controllers.orch_ctrl.AppConfig.get_emulators_path", return_value=str(emu_path)):
            result = orch_ctrl._find_emulator_executable(emu_id)
            assert result is None
