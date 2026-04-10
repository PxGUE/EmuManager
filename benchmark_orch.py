import time
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Mock dependencies
for mod in ["PySide6", "PySide6.QtCore", "PySide6.QtWidgets", "PySide6.QtQuick", "psutil", "pypresence"]:
    sys.modules[mod] = MagicMock()

# Basic mock for QObject so inheritance works
class QObjectMock:
    def __init__(self, *args, **kwargs):
        pass
sys.modules["PySide6.QtCore"].QObject = QObjectMock
sys.modules["PySide6.QtCore"].Signal = MagicMock
sys.modules["PySide6.QtCore"].Slot = lambda *args, **kwargs: (lambda func: func)

# Add current dir and emumanager to sys.path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "emumanager"))

from emumanager.controllers.orch_ctrl import OrchestraController

def benchmark():
    # Mock dependencies
    db = MagicMock()
    libretro = MagicMock()

    # We need to make sure AppConfig is initialized or mocked
    from emumanager.core.config import AppConfig

    # Setup some dummy emulator paths
    base_emu_path = Path("/tmp/emulators_test")
    base_emu_path.mkdir(parents=True, exist_ok=True)

    # Create some files to simulate installed emulators
    (base_emu_path / "retroarch").mkdir(exist_ok=True)
    (base_emu_path / "retroarch" / "RetroArch-Win64").mkdir(exist_ok=True)
    (base_emu_path / "retroarch" / "RetroArch-Win64" / "retroarch.exe").touch()

    (base_emu_path / "dolphin").mkdir(exist_ok=True)
    (base_emu_path / "dolphin" / "Dolphin.exe").touch()

    # Mocking AppConfig.get_asset_path to return a real path for repositories.json
    AppConfig.get_asset_path = MagicMock(return_value=Path("emumanager/resources/repositories.json"))
    AppConfig.get_emulators_path = MagicMock(return_value=str(base_emu_path))

    ctrl = OrchestraController(db, libretro)

    # Pre-warm
    ctrl.get_emulator_repositories()

    start = time.perf_counter()
    iterations = 1000
    for _ in range(iterations):
        ctrl.get_emulator_repositories()
    end = time.perf_counter()

    print(f"Time for {iterations} calls: {end - start:.4f}s")
    print(f"Average time per call: {(end - start) / iterations * 1000:.4f}ms")

if __name__ == "__main__":
    benchmark()
