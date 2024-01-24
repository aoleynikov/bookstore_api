import pytest
from unittest.mock import Mock
from handlers.auth_handlers import LoginHandler
from presenters import TokenPairPresenter
from exceptions import UnauthenticatedException
from models.user import TokenPair
import uuid


class TestLoginHandler:
    def test_login_handler(self):
        validator = Mock()
        presenter = TokenPairPresenter()
        auth_service = Mock()

        handler = LoginHandler(validator, presenter, auth_service)

        request = Mock()
        attributes = {"email": "test@example.com", "password": "password"}
        request.json = attributes

        auth_service.login.return_value = TokenPair("access", "refresh")

        result = handler.handle(request)

        auth_service.login.assert_called_once_with(
            attributes["email"], attributes["password"]
        )

        assert result.status_code == 200
        assert result.json == {"access_token": "access", "refresh_token": "refresh"}

    def test_login_handler_authentication_failure(self):
        validator = Mock()
        presenter = TokenPairPresenter()
        auth_service = Mock()

        handler = LoginHandler(validator, presenter, auth_service)

        request = Mock()
        attributes = {
            "email": "test@example.com",
            "password": "wrong_password",
        }
        request.json = attributes

        auth_service.login.side_effect = UnauthenticatedException()

        result = handler.handle(request)

        auth_service.login.assert_called_once_with(
            attributes["email"], attributes["password"]
        )
        
        assert result.status_code == 401
        assert result.json == {}
