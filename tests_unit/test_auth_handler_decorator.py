from unittest.mock import Mock, patch
from handlers.common import (
    AuthDecorator,
    Auth,
    UnauthenticatedException,
    UnauthorizedException,
)
from flask import Response


def test_auth_decorator_authenticated_and_authorized():
    auth_service = Mock()
    policy = Auth(roles=["user"], allow_anonymous=False)
    decoratee = Mock()
    request = Mock()
    request.headers = {}

    auth_decorator = AuthDecorator(auth_service, policy, decoratee)

    result = auth_decorator.handle(request)

    decoratee.handle.assert_called_once()
    assert result == decoratee.handle.return_value


def test_auth_decorator_unauthenticated():
    auth_service = Mock()
    auth_service.authenticate.side_effect = UnauthenticatedException
    policy = Auth(roles=["user"], allow_anonymous=False)
    decoratee = Mock()
    request = Mock()
    request.headers = {}

    auth_decorator = AuthDecorator(auth_service, policy, decoratee)

    result = auth_decorator.handle(request)

    assert isinstance(result, Response)
    assert result.status_code == 401


def test_auth_decorator_unauthorized():
    auth_service = Mock()
    auth_service.authorize.side_effect = UnauthorizedException
    policy = Auth(roles=["user"], allow_anonymous=False)
    decoratee = Mock()
    request = Mock()
    request.headers = {}

    auth_decorator = AuthDecorator(auth_service, policy, decoratee)

    result = auth_decorator.handle(request)

    assert isinstance(result, Response)
    assert result.status_code == 403
