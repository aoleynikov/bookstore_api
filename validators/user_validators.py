from .common import BaseValidator, BaseKeyValidator


class EmailUniqueValidator(BaseKeyValidator):
    def __init__(self, key: str, users_repository) -> None:
        super().__init__(key)
        self.users_repository = users_repository

    def is_valid(self, args: dict) -> bool:
        value = args.get(self.key, "")
        return self.users_repository.find_by_email(value) is None

    def error(self) -> dict:
        return {"message": "Already taken", "key": "error_email_already_taken"}


class PasswordsMatchValidator(BaseKeyValidator):
    def __init__(self, key, matching_key):
        super().__init__(key)
        self.matching_key = matching_key

    def is_valid(self, args: dict) -> bool:
        return args.get(self.key) == args.get(self.matching_key)

    def error(self) -> dict:
        return {"message": "Passwords should match", "key": "error_password_mismatch"}
