from .common import BaseHandler


class RegisterHandler(BaseHandler):
    def __init__(self, validator, presenter, users_service, auth_service):
        super().__init__(validator, presenter)
        self.users_service = users_service
        self.auth_service = auth_service
        self.success_code = 201

    def execute(self, request):
        body = request.json

        email = body.get("email")
        password = body.get("password")

        user = self.users_service.create({"email": email, "password": password})
        token_pair = self.auth_service.login(user.email, password)

        return token_pair
