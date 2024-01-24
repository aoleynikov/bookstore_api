from bson import ObjectId
from datetime import datetime, timedelta
import random

from exceptions import (
    UnauthenticatedException,
    UnauthorizedException,
    InvalidRequestException,
)
from models.user import TokenPair, PasswordResetRequest


class AuthService:
    def __init__(
        self,
        users_repository,
        logout_repository,
        password_service,
        tokens_service,
    ):
        self.users_repository = users_repository
        self.logout_repository = logout_repository
        self.password_service = password_service
        self.tokens_service = tokens_service

    def login(self, email, password):
        user = self.users_repository.find_by_email(email)
        if not user:
            raise UnauthenticatedException()

        if not self.password_service.check(password, user.password_hash):
            raise UnauthenticatedException()

        new_pair = self.__create_pair(user)
        return new_pair

    def refresh(self, refresh_token):
        user = self.__get_user_by_token(refresh_token)
        if self.logout_repository.find_refresh(refresh_token):
            raise UnauthenticatedException()
        new_pair = self.__create_pair(user)
        return new_pair

    def logout(self, auth_header, refresh_token):
        access_token = self.__get_token_from_header(auth_header)
        model = TokenPair(access=access_token, refresh=refresh_token)
        self.logout_repository.save(model)

    def authenticate(self, auth_header, allow_anonymous):
        jwt = self.__get_token_from_header(auth_header, allow_anonymous)
        if not jwt:
            if allow_anonymous:
                return None
            else:
                raise UnauthenticatedException()
        if self.logout_repository.find_access(jwt):
            if allow_anonymous:
                return None
            else:
                raise UnauthenticatedException()
        user = self.__get_user_by_token(jwt, allow_anonymous)
        return user

    def authorize(self, user, roles):
        role = None
        if user:
            role = user.role
        if roles != "*" and role not in roles:
            raise UnauthorizedException()

    def __create_pair(self, user):
        claims = {"user_id": str(user.id), "role": user.role}
        access_token = self.tokens_service.encode("access", claims)
        refresh_token = self.tokens_service.encode("refresh", claims)
        return TokenPair(access_token, refresh_token)

    def __get_user_by_token(self, token, allow_anonymous=None):
        payload = self.tokens_service.decode(token)
        if not payload:
            if allow_anonymous:
                return None
            else:
                raise UnauthenticatedException()
        user_id = payload.get("user_id")
        user = self.users_repository.find_by_id(user_id)

        if not user:
            if allow_anonymous:
                return None
            else:
                raise UnauthenticatedException()

        return user

    def __get_token_from_header(self, auth_header, allow_anonymous=None):
        if not auth_header:
            if allow_anonymous:
                return None
            raise UnauthenticatedException()
        authorization = auth_header.split(" ")
        if len(authorization) != 2 or authorization[0].lower() != "bearer":
            if allow_anonymous:
                return None
            raise UnauthenticatedException()
        token = authorization[1]

        return token
