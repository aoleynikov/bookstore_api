from faker import Faker
from bson import ObjectId
from structure import structure
from app import app
from .factories import UserFactory


class TestRegistration:
    def setup_method(self):
        self.client = app.test_client()
        self.context = app.app_context()
        self.context.push()

        self.fake = Faker()
        self.users_repository = structure.users_repository
        self.users_repository.delete_all()

    def teardown_method(self):
        self.context.pop()
        self.users_repository.delete_all()

    def test_register_valid(self):
        email = self.fake.email()
        password = self.fake.password()
        attributes = {
            "email": email,
            "password": password,
            "password_confirmation": password,
        }

        response = self.client.post("/users/", json=attributes)

        assert response.status_code == 201

        assert response.json["access_token"]
        assert response.json["refresh_token"]

        created_user = self.users_repository.find_by_email(email)
        assert created_user

    def test_register_invalid_email(self):
        email = "invalid_email"
        password = self.fake.password()
        attributes = {
            "email": email,
            "password": password,
            "password_confirmation": password,
        }

        response = self.client.post("/users/", json=attributes)

        assert response.status_code == 400
        assert "Invalid format" in response.json["email"][0]["message"]

    def test_register_passwords_dont_match(self):
        email = self.fake.email()
        password = self.fake.password()
        attributes = {
            "email": email,
            "password": password,
            "password_confirmation": password + "extra",
        }

        response = self.client.post("/users/", json=attributes)

        assert response.status_code == 400
        assert "Passwords should match" in response.json["password"][0]["message"]

    def test_register_existing_user(self):
        email = self.fake.email()
        password = self.fake.password()
        attributes = {
            "email": email,
            "password": password,
            "password_confirmation": password,
        }

        self.client.post("/users/", json=attributes)

        response = self.client.post("/users/", json=attributes)

        assert response.status_code == 400
        assert "Already taken" in response.json["email"][0]["message"]


class TestTokens:
    def setup_method(self):
        self.client = app.test_client()
        self.context = app.app_context()
        self.context.push()

        self.fake = Faker()
        self.users_repository = structure.users_repository
        self.users_repository.delete_all()

    def teardown_method(self):
        self.context.pop()
        self.users_repository.delete_all()

    def test_login_valid(self):
        email = self.fake.email()
        password = self.fake.password()
        attributes = {
            "email": email,
            "password": password,
        }

        UserFactory.create_user(**attributes)
        response = self.client.post("/auth/login", json=attributes)

        assert response.status_code == 200

        assert response.json["access_token"]
        assert response.json["refresh_token"]

    def test_refresh_valid(self):
        email = self.fake.email()
        password = self.fake.password()
        attributes = {
            "email": email,
            "password": password,
        }

        UserFactory.create_user(**attributes)
        login_response = self.client.post("/auth/login", json=attributes)

        assert login_response.status_code == 200
        refresh_token = login_response.json["refresh_token"]

        refresh_response = self.client.post(
            "/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert refresh_response.status_code == 200
        assert refresh_response.json["access_token"]
        assert refresh_response.json["refresh_token"]