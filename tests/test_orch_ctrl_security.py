import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from emumanager.controllers.orch_ctrl import OrchestraController

@pytest.fixture
def orchestra_controller():
    db = MagicMock()
    libretro = MagicMock()
    return OrchestraController(db, libretro)

def test_uninstall_emulator_security_traversal(orchestra_controller):
    # Mock AppConfig para que devuelva una ruta base conocida
    with patch("emumanager.core.config.AppConfig.get_emulators_path", return_value="/app/data/emulators"):
        # Intento de desinstalar algo fuera de la ruta base
        # El emu_id malicioso
        emu_id = "../../forbidden"

        result = orchestra_controller.uninstall_emulator(emu_id)

        assert result is False

def test_install_emulator_security_traversal(orchestra_controller):
    with patch("emumanager.core.config.AppConfig.get_emulators_path", return_value="/app/data/emulators"):
        emu_id = "../malicious"
        result = orchestra_controller.install_emulator(emu_id, "http://evil.com/malicious.zip", "evil.exe")

        assert result is False

def test_find_emulator_executable_security_traversal(orchestra_controller):
    with patch("emumanager.core.config.AppConfig.get_emulators_path", return_value="/app/data/emulators"):
        # Este es un método privado pero lo testeamos para asegurar la seguridad
        emu_id = "../../../etc"
        result = orchestra_controller._find_emulator_executable(emu_id)

        assert result is None
