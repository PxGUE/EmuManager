import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from emumanager.backend.libretro import LibretroManager

@pytest.fixture
def libretro_manager(tmp_path):
    return LibretroManager(emus_base_path=tmp_path)

def test_download_core_security_traversal(libretro_manager, tmp_path):
    # Intentamos descargar un core para una plataforma maliciosa
    # Para esto necesitamos mockear _get_platform_for_core o pasar un core que mapee a algo malo

    with patch.object(LibretroManager, "_get_platform_for_core", return_value="../../malicious"):
        result = libretro_manager.download_core("some_core")
        assert result is None

def test_uninstall_core_security_traversal(libretro_manager, tmp_path):
    # Intentamos desinstalar un core de una plataforma maliciosa
    with patch.object(LibretroManager, "_get_platform_for_core", return_value="../forbidden"):
        result = libretro_manager.uninstall_core("some_core")
        assert result is False
