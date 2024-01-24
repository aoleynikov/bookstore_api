import re
from bson import ObjectId
from abc import ABC, abstractmethod


class BaseValidator(ABC):
    @abstractmethod
    def is_valid(self, args) -> None:
        pass

    @abstractmethod
    def error(self) -> None:
        pass


class BaseKeyValidator(BaseValidator):
    def __init__(self, key: str) -> None:
        self.key = key


class EmailRegexValidator(BaseKeyValidator):
    def is_valid(self, args: dict) -> bool:
        if self.key not in args or not args[self.key]:
            return True
        value = args[self.key]
        # Match: @ sign, and at least one . in the part after the @ w/o white spaces
        if re.match(r"^[^\s]+@[^\s]+\.[^\s]+$", value):
            return True
        return False

    def error(self) -> dict:
        return {"message": "Invalid format", "key": "error_email_invalid_format"}


class PresenceValidator(BaseKeyValidator):
    def is_valid(self, args: dict) -> bool:
        value = args.get(self.key)
        return value is not None and value != "" and value != [] and value != {}

    def error(self) -> dict:
        return {"message": "Has to be present", "key": "error_presence"}


class IntegerValidator(BaseKeyValidator):
    def is_valid(self, args: dict) -> bool:
        value = args.get(self.key)
        return value is not None and isinstance(value, int)

    def error(self) -> dict:
        return {"message": "Has to be an integer", "key": "error_number"}
    
class PositiveValidator(BaseKeyValidator):
    def is_valid(self, args: dict) -> bool:
        value = args.get(self.key)
        return value is not None and value > 0

    def error(self) -> dict:
        return {"message": "Must be positive", "key": "error_positive"}

class LengthValidator(BaseKeyValidator):
    def __init__(self, key, min_length, max_length):
        super().__init__(key)
        self.min_length = min_length
        self.max_length = max_length

    def is_valid(self, args: dict) -> bool:
        value = args.get(self.key, "")
        return self.min_length <= len(value) <= self.max_length

    def error(self) -> dict:
        return {
            "message": f"Length must be between {self.min_length} and {self.max_length}",
            "key": "error_invalid_length",
        }
