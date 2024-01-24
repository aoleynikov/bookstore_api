from .common import BaseHandler


class LoginHandler(BaseHandler):
    def __init__(self, validator, presenter, auth_service):
        super().__init__(validator, presenter)
        self.auth_service = auth_service

    def execute(self, request, **kwargs):
        payload = request.json
        email = payload.get("email")
        password = payload.get("password")
        return self.auth_service.login(email, password)


class RefreshHandler(BaseHandler):
    def __init__(self, validator, presenter, auth_service):
        super().__init__(validator, presenter)
        self.auth_service = auth_service

    def execute(self, request, **kwargs):
        payload = request.json
        refresh_token = payload.get("refresh_token")
        return self.auth_service.refresh(refresh_token)


class LogoutHandler(BaseHandler):
    def __init__(self, validator, presenter, auth_service):
        super().__init__(validator, presenter)
        self.auth_service = auth_service

    def execute(self, request, **kwargs):
        auth_header = request.headers.get("Authorization")
        return self.auth_service.logout(auth_header)
