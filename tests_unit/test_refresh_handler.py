import pytest
from unittest.mock import Mock
from handlers.auth_handlers import RefreshHandler
from presenters import TokenPairPresenter
from exceptions import UnauthenticatedException
from models.user import TokenPair
import uuid


class TestRefreshHandler:
    def test_refresh_handler(self):
        validator = Mock()
        presenter = TokenPairPresenter()
        auth_service = Mock()

        handler = RefreshHandler(validator, presenter, auth_service)

        request = Mock()
        request.json = {"refresh_token": "old_refresh"}

        auth_service.refresh.return_value = TokenPair("new_access", "old_refresh")

        result = handler.handle(request)

        auth_service.refresh.assert_called_once_with(request.json["refresh_token"])

        assert result.status_code == 200
        assert result.json == {
            "access_token": "new_access",
            "refresh_token": "old_refresh",
        }

    def test_refresh_handler_authentication_failure(self):
        validator = Mock()
        presenter = TokenPairPresenter()
        auth_service = Mock()

        handler = RefreshHandler(validator, presenter, auth_service)

        request = Mock()
        request.json = {"refresh_token": "wrong_refresh"}

        auth_service.refresh.side_effect = UnauthenticatedException()

        result = handler.handle(request)

        auth_service.refresh.assert_called_once_with(request.json["refresh_token"])

        assert result.status_code == 401
        assert result.json == {}
