import uuid
from structure import structure


class UserFactory:
    @staticmethod
    def create_user(**kwargs):
        default_args = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "password": "password",
        }
        default_args.update(kwargs)
        return structure.users_service.create(default_args)

    @staticmethod
    def create_admin(**kwargs):
        user = UserFactory.create_user(**kwargs)
        return structure.users_service.update(user.id, {"role": "admin"})

    @staticmethod
    def sign_in(email, password="password"):
        return structure.auth_service.login(email, password)


class InventoryFactory:
    @staticmethod
    def create_inventory(**kwargs):
        default_args = {"author": f"author_{uuid.uuid4()}", "title": f"title_{uuid.uuid4()}", "quantity": 1, "price": 1050}
        default_args.update(kwargs)
        return structure.inventory_service.create(default_args)