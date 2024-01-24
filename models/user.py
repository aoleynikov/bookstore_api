from datetime import datetime
from random import choice, randint
from string import ascii_uppercase


class User:
    def __init__(self) -> None:
        self.id = None
        self.email = None
        self.role = None
        self.password_hash = None
        self.token_pairs = None
        self.password_reset_requests = None
        self.profile = None
        self.created_at = None
        self.email_confirmed = False

    @staticmethod
    def from_request(attributes: dict):
        user = User()
        user.email = attributes["email"]
        user.role = attributes.get("role", "user")
        user.password_hash = attributes["password_hash"]
        user.password_reset_requests = []
        user.profile = Profile.from_request(attributes.get("profile", {}))
        user.created_at = datetime.utcnow()
        return user

    def assign_request(self, attributes: dict) -> None:
        if "email" in attributes:
            self.email = attributes["email"]
        if "role" in attributes:
            self.role = attributes["role"]
        if "profile" in attributes:
            self.profile.assign_request(attributes["profile"])


class TokenPair:
    def __init__(self, access, refresh):
        self.access = access
        self.refresh = refresh


class PasswordResetRequest:
    def __init__(self) -> None:
        self.code = "".join(choice(ascii_uppercase) for i in range(6))
        self.created_at = datetime.utcnow()


class Profile:
    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.avatar = None

    @staticmethod
    def from_request(attributes: dict):
        profile = Profile()
        profile.first_name = attributes.get("first_name")
        profile.last_name = attributes.get("last_name")
        avatar_attributes = attributes.get("avatar")
        if avatar_attributes:
            profile.avatar = UploadedFile(
                avatar_attributes.get("key"), avatar_attributes.get("filename")
            )
        return profile

    def assign_request(self, attributes: dict) -> None:
        avatar_attributes = attributes.get("avatar")
        if avatar_attributes:
            self.avatar = UploadedFile(
                avatar_attributes.get("key"), avatar_attributes.get("filename")
            )
        self.first_name = attributes.get("first_name")
        self.last_name = attributes.get("last_name")

    def get_files(self):
        files = []
        if self.avatar:
            files.append(self.avatar)
        return files
