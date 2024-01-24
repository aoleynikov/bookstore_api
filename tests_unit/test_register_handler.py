from unittest.mock import Mock
from handlers.user_handlers import RegisterHandler
from presenters import TokenPairPresenter
from models.user import TokenPair
from exceptions import InvalidRequestException
import uuid


class TestRegissterHandler:
    def test_register_handler(self):
        validator = Mock()
        presenter = TokenPairPresenter()
        users_service = Mock()
        auth_service = Mock()

        handler = RegisterHandler(validator, presenter, users_service, auth_service)

        request = Mock()
        request.json = {
            "email": "test@example.com",
            "password": "password",
        }

        users_service.create.return_value = Mock(email=request.json["email"])
        auth_service.login.return_value = TokenPair("access", "refresh")

        result = handler.handle(request)

        users_service.create.assert_called_once_with(request.json)
        auth_service.login.assert_called_once_with(
            request.json["email"], request.json["password"]
        )

        assert result.status_code == 201
        assert result.json == {"access_token": "access", "refresh_token": "refresh"}

    def test_register_handler_validation_failure(self):
        validator = Mock()
        presenter = TokenPairPresenter()
        users_service = Mock()
        auth_service = Mock()

        handler = RegisterHandler(validator, presenter, users_service, auth_service)

        request = Mock()
        request.json.return_value = {"email": "", "password": "password"}

        validator.validate.side_effect = InvalidRequestException(
            {"email": ["Has to be present"]}
        )

        result = handler.handle(request)

        users_service.create.assert_not_called()
        auth_service.login.assert_not_called()

        assert result.status_code == 400
        assert result.json == {"email": ["Has to be present"]}
