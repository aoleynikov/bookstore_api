from unittest.mock import Mock
from services import AuthService
from exceptions import UnauthenticatedException
from models.user import TokenPair
import pytest
import uuid


def test_login_success():
    users_repository = Mock()
    password_service = Mock()
    tokens_service = Mock()
    logout_repository = Mock()
    auth_service = AuthService(
        users_repository, logout_repository, password_service, tokens_service
    )

    email = "test@example.com"
    password = "password"
    user = Mock()
    password_service.check.return_value = True
    users_repository.find_by_email.return_value = user
    result = auth_service.login(email, password)

    assert result is not None
    assert result.access is not None
    assert result.refresh is not None

def test_login_unauthenticated_exception():
    users_repository = Mock()
    password_service = Mock()
    tokens_service = Mock()
    logout_repository = Mock()
    auth_service = AuthService(
        users_repository, logout_repository, password_service, tokens_service
    )

    email = "test@example.com"
    password = "password"
    password_service.check.return_value = False
    users_repository.find_by_email.return_value = None

    with pytest.raises(UnauthenticatedException):
        auth_service.login(email, password)


def test_refresh_success():
    users_repository = Mock()
    password_service = Mock()
    tokens_service = Mock()
    logout_repository = Mock()
    auth_service = AuthService(
        users_repository, logout_repository, password_service, tokens_service
    )

    refresh_token = "refresh_token"
    user = Mock()
    user.id = str(uuid.uuid4())
    logout_repository.find_refresh.return_value = None
    tokens_service.decode.return_value = {"user_id": user.id}
    tokens_service.encode.return_value = "token"
    users_repository.find_by_id.return_value = user
    result = auth_service.refresh(refresh_token)

    assert result is not None
    assert result.access == "token"
    assert result.refresh == "token"


def test_refresh_unauthenticated():
    users_repository = Mock()
    password_service = Mock()
    tokens_service = Mock()
    logout_repository = Mock()
    auth_service = AuthService(
        users_repository, logout_repository, password_service, tokens_service
    )

    refresh_token = "refresh_token"
    tokens_service.decode.side_effect = UnauthenticatedException()
    logout_repository.find_refresh.return_value = None

    with pytest.raises(UnauthenticatedException):
        auth_service.refresh(refresh_token)


def test_logout_success():
    users_repository = Mock()
    password_service = Mock()
    tokens_service = Mock()
    logout_repository = Mock()
    auth_service = AuthService(
        users_repository, logout_repository, password_service, tokens_service
    )

    auth_header = "Bearer access_token"
    refresh_token = "refresh_token"
    auth_service.logout(auth_header, refresh_token)

    logout_repository.save.assert_called_once()
