class BaseAppException(Exception):
    pass


class InvalidRequestException(BaseAppException):
    def __init__(self, errors: dict) -> None:
        self.errors = errors


class VariableNotFoundException(BaseAppException):
    pass


class UnauthenticatedException(BaseAppException):
    pass


class NotFoundException(BaseAppException):
    pass


class UnauthorizedException(BaseAppException):
    pass


class ConflictRequestException(BaseAppException):
    pass
