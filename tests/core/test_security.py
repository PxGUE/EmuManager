import pytest
from core.security import CredentialsManager

def test_save_user_password(mocker):
    mock_set_password = mocker.patch("core.security.keyring.set_password")

    service = "test_service"
    username = "test_user"
    password = "test_password"

    CredentialsManager.save_user_password(service, username, password)

    mock_set_password.assert_called_once_with(service, username, password)

def test_get_user_password_success(mocker):
    mock_get_password = mocker.patch("core.security.keyring.get_password", return_value="secret")

    service = "test_service"
    username = "test_user"

    result = CredentialsManager.get_user_password(service, username)

    assert result == "secret"
    mock_get_password.assert_called_once_with(service, username)

def test_get_user_password_not_found(mocker):
    mock_get_password = mocker.patch("core.security.keyring.get_password", return_value=None)

    service = "test_service"
    username = "test_user"

    result = CredentialsManager.get_user_password(service, username)

    assert result is None
    mock_get_password.assert_called_once_with(service, username)
