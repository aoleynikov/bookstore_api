import json
from flask import Response
from exceptions import (
    InvalidRequestException,
    NotFoundException,
    UnauthorizedException,
    UnauthenticatedException,
)
from collections import defaultdict


class BaseHandler:
    def __init__(self, validator=None, presenter=None):
        self.validator = validator
        self.presenter = presenter
        self.success_code = 200

    def execute(self, request, **kwargs):
        raise NotImplementedError()

    def handle(self, request, **kwargs):
        try:
            if self.validator is not None:
                self.validator.validate(request)
            result = self.execute(request, **kwargs)
            response_body = {}
            if result:
                response_body = self.presenter.present(result)
            response = self.render_response(response_body, status=self.success_code)
        except InvalidRequestException as e:
            response = self.render_response(e.errors, status=400)
        except UnauthorizedException:
            response = self.render_response(
                {"message": "access_not_allowed"}, status=403
            )
        except NotFoundException:
            response = self.render_response({}, status=404)
        except UnauthenticatedException:
            response = self.render_response({}, status=401)
        return response

    def render_response(self, response, status=200):
        return Response(
            json.dumps(response),
            status=status,
            mimetype="application/json",
        )


class RequestValidator:
    def __init__(self, validators: list) -> None:
        self.validators = validators

    def validate(self, request) -> None:
        errors = defaultdict(list)
        args = request.json

        for validator in self.validators:
            if validator.is_valid(args):
                continue
            errors[validator.key].append(validator.error())

        if errors:
            raise InvalidRequestException(errors)



class Auth:
    def __init__(self, roles, allow_anonymous=False):
        self.roles = roles
        self.allow_anonymous = allow_anonymous


class AuthDecorator:
    def __init__(self, auth_service, policy, decoratee):
        self.auth_service = auth_service
        self.policy = policy
        self.decoratee = decoratee

    def handle(self, request, **kwargs):
        auth_header = request.headers.get("Authorization")
        user = None
        try:
            user = self.auth_service.authenticate(
                auth_header, self.policy.allow_anonymous
            )
            self.auth_service.authorize(user, self.policy.roles)
        except UnauthenticatedException:
            return Response(response="{}", status=401)
        except UnauthorizedException:
            return Response(response="{}", status=403)
        kwargs["principal"] = user
        return self.decoratee.handle(request, **kwargs)


class UploadFileHandler(BaseHandler):
    def __init__(self, validator=None, presenter=None, file_service=None):
        super().__init__(validator, presenter)
        self.file_service = file_service

    def execute(self, request, **kwargs):
        file = request.files.get("file")
        if not file:
            raise InvalidRequestException({})
        filename = file.filename
        data = file.readbytes()
        return self.file_service.create_temp_file(filename, data)
