import pytest
from pathlib import Path
from unittest.mock import patch
from emumanager.app import init_storage

def test_init_storage_creates_all_directories(tmp_path):
    """Verifica que init_storage cree todos los subdirectorios necesarios."""
    test_data_dir = tmp_path / "emu_data"

    # No es necesario crear test_data_dir porque mkdir(parents=True) lo hará si es necesario
    # pero AppConfig.get_app_data_dir() normalmente ya asegura que data_dir existe.
    # Aquí simulamos el retorno de AppConfig.get_app_data_dir()

    with patch("emumanager.app.AppConfig.get_app_data_dir", return_value=test_data_dir):
        init_storage()

    # Verificar subdirectorios
    expected_subdirs = ["db", "media", "logs", "temp"]
    for sub in expected_subdirs:
        subdir_path = test_data_dir / sub
        assert subdir_path.exists(), f"El subdirectorio {sub} no fue creado"
        assert subdir_path.is_dir(), f"{sub} no es un directorio"

def test_init_storage_handles_existing_directories(tmp_path):
    """Verifica que init_storage no falle si los directorios ya existen."""
    test_data_dir = tmp_path / "emu_data"
    test_data_dir.mkdir(parents=True)

    # Crear uno de los subdirectorios de antemano
    (test_data_dir / "db").mkdir()

    with patch("emumanager.app.AppConfig.get_app_data_dir", return_value=test_data_dir):
        # No debería lanzar OSError gracias a exist_ok=True
        init_storage()

    # Verificar que todos existen al final
    expected_subdirs = ["db", "media", "logs", "temp"]
    for sub in expected_subdirs:
        assert (test_data_dir / sub).exists()
