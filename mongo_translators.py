from models.user import User, TokenPair, PasswordResetRequest, Profile
from models.inventory import InventoryItem, InventoryAlert


class UserTranslator:
    def __init__(
        self,
        tokens_pair_translator,
        password_reset_request_translator,
        profile_translator,
    ):
        self.tokens_pair_translator = tokens_pair_translator
        self.password_reset_request_translator = password_reset_request_translator
        self.profile_translator = profile_translator

    def to_document(self, user) -> dict:
        password_reset_requests = [
            self.password_reset_request_translator.to_document(prr)
            for prr in user.password_reset_requests
        ]
        return {
            "_id": user.id,
            "email": user.email,
            "role": user.role,
            "password_hash": user.password_hash,
            "password_reset_requests": password_reset_requests,
            "profile": self.profile_translator.to_document(user.profile),
            "created_at": user.created_at,
            "email_confirmed": user.email_confirmed,
        }

    def from_document(self, document: dict) -> User:
        user = User()
        user.id = document["_id"]
        user.email = document["email"]
        user.role = document["role"]
        user.password_hash = document["password_hash"]
        user.password_reset_requests = [
            self.password_reset_request_translator.from_document(prr)
            for prr in document.get("password_reset_requests", [])
        ]
        user.profile = self.profile_translator.from_document(document.get("profile"))
        user.created_at = document.get("created_at")
        user.email_confirmed = document.get("email_confirmed")
        return user


class TokenPairTranslator:
    def from_document(self, document) -> TokenPair:
        return TokenPair(
            document.get("id"),
            document.get("access_token"),
            document.get("refresh_token"),
        )

    def to_document(self, tokens_pair) -> dict:
        return {
            "id": tokens_pair.id,
            "access_token": tokens_pair.access,
            "refresh_token": tokens_pair.refresh,
        }


class PasswordResetRequestTranslator:
    def from_document(self, document) -> PasswordResetRequest:
        result = PasswordResetRequest()
        result.code = document.get("code")
        result.created_at = document.get("created_at")
        return result

    def to_document(self, password_reset_request) -> dict:
        return {
            "code": password_reset_request.code,
            "created_at": password_reset_request.created_at,
        }


class ProfileTranslator:
    def from_document(self, document) -> Profile:
        result = Profile()
        result.first_name = document.get("first_name")
        result.last_name = document.get("last_name")
        return result

    def to_document(self, profile) -> dict:
        return {"first_name": profile.first_name, "last_name": profile.last_name}


class InventoryItemTranslator:
    def __init__(self, inventory_alert_translator):
        self.inventory_alert_translator = inventory_alert_translator

    def from_document(self, document) -> InventoryItem:
        result = InventoryItem()
        result.id = document.get("_id")
        result.name = document.get("author")
        result.title = document.get("title")
        result.price = document.get("price")
        result.quantity = document.get("quantity")
        result.alert = self.inventory_alert_translator.from_document(
            document.get("alert")
        )
        result.created_at = document.get("created_at")
        return result

    def to_document(self, inventory_item) -> dict:
        return {
            "_id": inventory_item.id,
            "author": inventory_item.author,
            "title": inventory_item.title,
            "price": inventory_item.price,
            "quantity": inventory_item.quantity,
            "alert": self.inventory_alert_translator.to_document(inventory_item.alert),
            "created_at": inventory_item.created_at,
        }
    

class InventoryAlertTranslator:
    def from_document(self, document) -> InventoryAlert:
        if not document:
            return None
        result = InventoryAlert()
        result.quantity = document.get("quantity")
        return result

    def to_document(self, inventory_alert) -> dict:
        if not inventory_alert:
            return None
        return {"quantity": inventory_alert.quantity}