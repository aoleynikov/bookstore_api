from faker import Faker
from bson import ObjectId
from structure import structure
from app import app
from .factories import UserFactory, InventoryFactory


class InventoryIntegrationTest:
    def setup_method(self):
        self.client = app.test_client()
        self.context = app.app_context()
        self.context.push()

        self.fake = Faker()
        self.users_repository = structure.users_repository
        self.users_repository.delete_all()
        self.inventory_repository = structure.inventory_repository
        self.inventory_repository.delete_all()

        self.user = UserFactory.create_user()
        jwt_claim = {"user_id": str(self.user.id)}
        self.access_token = structure.tokens_service.encode("access", jwt_claim)

    def teardown_method(self):
        self.context.pop()
        self.users_repository.delete_all()
        self.inventory_repository.delete_all()


class TestGetInventoryList(InventoryIntegrationTest):
    def test_get_inventory_list(self):
        models = []
        for i in range(10):
            add = InventoryFactory.create_inventory()
            models.append(add)

        response = self.client.get("/inventory/", headers={"Authorization": f"Bearer {self.access_token}"})

        assert response.status_code == 200

        assert len(response.json) == 10
        model_ids = [str(model.id) for model in models]
        response_ids = [str(model["id"]) for model in response.json]
        assert set(model_ids) == set(response_ids)


class TestCreateInventoryItem(InventoryIntegrationTest):
    def test_create_valid_inventory_item(self):
        attributes = {
            "author": self.fake.name(),
            "title": self.fake.word(),
            "price": 1050,
            "quantity": self.fake.pyint(),
        }

        response = self.client.post("/inventory/", json=attributes, headers={"Authorization": f"Bearer {self.access_token}"})

        assert response.status_code == 201
        assert response.json["id"]
        assert response.json["author"] == attributes["author"]
        assert response.json["title"] == attributes["title"]
        assert response.json["price"] == attributes["price"]
        assert response.json["quantity"] == attributes["quantity"]

        inventory_item = self.inventory_repository.find_by_id(response.json["id"])
        assert str(inventory_item.id) == response.json["id"]

    def test_attempt_with_invalid_payload(self):
        attributes = {
            "author": self.fake.name(),
            "title": self.fake.word(),
            "price": 1050,
        }

        response = self.client.post("/inventory/", json=attributes, headers={"Authorization": f"Bearer {self.access_token}"})

        assert response.status_code == 400
        assert response.json["quantity"][0]["message"] == "Has to be present"

    def test_attempt_with_invalid_price(self):
        attributes = {
            "author": self.fake.name(),
            "title": self.fake.word(),
            "price": "invalid_price",
            "quantity": self.fake.pyint(),
        }

        response = self.client.post("/inventory/", json=attributes, headers={"Authorization": f"Bearer {self.access_token}"})

        assert response.status_code == 400
        assert response.json["price"][0]["message"] == "Has to be an integer"

class TestUpdateInventoryItem(InventoryIntegrationTest):
    def test_update_inventory_item(self):
        inventory_item = InventoryFactory.create_inventory()
        attributes = {
            "author": self.fake.name(),
            "title": self.fake.word(),
            "price": inventory_item.price + 100,
            "quantity": self.fake.pyint(),
        }

        response = self.client.put(f"/inventory/{str(inventory_item.id)}", json=attributes, headers={"Authorization": f"Bearer {self.access_token}"})

        assert response.status_code == 200
        assert response.json["id"]
        assert response.json["author"] == attributes["author"]
        assert response.json["title"] == attributes["title"]
        assert response.json["price"] == attributes["price"]
        assert response.json["quantity"] == attributes["quantity"]

        inventory_item = self.inventory_repository.find_by_id(response.json["id"])
        assert str(inventory_item.id) == response.json["id"]

    def test_update_invalid_inventory_item(self):
        inventory_item = InventoryFactory.create_inventory()
        attributes = {
            "author": self.fake.name(),
            "title": self.fake.word(),
            "price": "invalid_price",
            "quantity": self.fake.pyint(),
        }

        response = self.client.put(f"/inventory/{str(inventory_item.id)}", json=attributes, headers={"Authorization": f"Bearer {self.access_token}"})

        assert response.status_code == 400
        assert response.json["price"][0]["message"] == "Has to be an integer"

class TestDeleteInventoryItem(InventoryIntegrationTest):
    def test_delete_inventory_item(self):
        inventory_item = InventoryFactory.create_inventory()

        response = self.client.delete(f"/inventory/{str(inventory_item.id)}", headers={"Authorization": f"Bearer {self.access_token}"})

        assert response.status_code == 204

        inventory_item = self.inventory_repository.find_by_id(inventory_item.id)
        assert inventory_item is None

    def test_delete_invalid_inventory_item(self):
        inventory_item = InventoryFactory.create_inventory()

        response = self.client.delete(f"/inventory/{str(ObjectId())}", headers={"Authorization": f"Bearer {self.access_token}"})

        assert response.status_code == 404


class TestCreateInventoryAlert(InventoryIntegrationTest):
    def test_create_valid_inventory_alert(self):
        inventory_item = InventoryFactory.create_inventory()
        attributes = {
            "quantity": 100,
        }

        response = self.client.put(f"/inventory/{str(inventory_item.id)}/alert", json=attributes, headers={"Authorization": f"Bearer {self.access_token}"})

        assert response.status_code == 201
        assert response.json["quantity"] == attributes["quantity"]

        updated_item = self.inventory_repository.find_by_id(inventory_item.id)
        assert updated_item.alert is not None
        

    def test_create_invalid_inventory_alert(self):
        inventory_item = InventoryFactory.create_inventory()
        attributes = {
            "quantity": -100,
        }

        response = self.client.put(f"/inventory/{str(inventory_item.id)}/alert", json=attributes, headers={"Authorization": f"Bearer {self.access_token}"})

        assert response.status_code == 400
        assert response.json["quantity"][0]["message"] == "Must be positive"

        updated_item = self.inventory_repository.find_by_id(inventory_item.id)
        assert updated_item.alert is None