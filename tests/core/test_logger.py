import pytest
from emumanager.core.logger import log_system_info

def test_log_system_info_happy_path(mocker):
    # Mock dependencies
    mock_psutil = mocker.patch("emumanager.core.logger.psutil")
    mock_platform = mocker.patch("emumanager.core.logger.platform")
    mock_sys = mocker.patch("emumanager.core.logger.sys")
    mock_app_config = mocker.patch("emumanager.core.logger.AppConfig")
    mock_emulog = mocker.patch("emumanager.core.logger.EmuLog")

    # Setup mock returns
    mock_psutil.virtual_memory.return_value.total = 16 * 1024**3 # 16GB
    mock_psutil.cpu_count.return_value = 8
    mock_platform.system.return_value = "Linux"
    mock_platform.release.return_value = "5.15.0"
    mock_platform.machine.return_value = "x86_64"
    mock_sys.version.split.return_value = ["3.10.12"]
    mock_app_config.APP_NAME = "EmuManager"
    mock_app_config.get_app_data_dir.return_value = "/mock/data/dir"

    # Call the function
    log_system_info()

    # Verify EmuLog.info calls
    expected_calls = [
        mocker.call("-" * 50),
        mocker.call("INICIANDO EmuManager (Ecosystem vM.A.N.G.O)"),
        mocker.call("OS: Linux 5.15.0 (x86_64)"),
        mocker.call("Python: 3.10.12"),
        mocker.call("CPU: 8 hilos | RAM: 16384MB"),
        mocker.call("Ruta Datos: /mock/data/dir"),
        mocker.call("-" * 50),
    ]
    mock_emulog.info.assert_has_calls(expected_calls, any_order=False)

def test_log_system_info_error_handling(mocker):
    # Mock psutil to raise an exception
    mocker.patch("emumanager.core.logger.psutil.virtual_memory", side_effect=Exception("Test Error"))
    mock_emulog = mocker.patch("emumanager.core.logger.EmuLog")

    # Call the function - should not raise exception
    log_system_info()

    # Verify EmuLog.warning was called
    mock_emulog.warning.assert_called_once()
    args, _ = mock_emulog.warning.call_args
    assert "No se pudo recolectar info del sistema: Test Error" in args[0]
