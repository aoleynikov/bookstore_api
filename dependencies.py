from typing import Any
import pymongo
import os
import requests
from dotenv import dotenv_values
from exceptions import VariableNotFoundException


class EnvironmentWrapper:
    def __init__(self):
        env = os.environ.get("ENV", "local")
        if env == "local":
            self.env_values = dotenv_values("secrets/local/.env")
        else:
            self.env_values = dotenv_values(".env")

    def get_var(self, key: str, fail_on_empty=True) -> str:
        try:
            return int(self.env_values[key])
        except KeyError:
            if fail_on_empty:
                raise VariableNotFoundException(f"{key} variable not found")
            else:
                return None
        except ValueError:
            return self.env_values[key]

    def read_file(self, file_path: str) -> str:
        with open(file_path) as file:
            content = file.read()
        return content


class PymongoWrapper:
    def __init__(self, environment_wrapper) -> None:
        self.username = environment_wrapper.get_var("MONGO_USERNAME")
        self.password = environment_wrapper.get_var("MONGO_PASSWORD")
        self.host = environment_wrapper.get_var("MONGO_HOST")
        self.port = environment_wrapper.get_var("MONGO_PORT")
        PymongoWrapper.client = self.get_client()
        self.name = environment_wrapper.get_var("MONGO_NAME")

    def get_client(self):
        credentials = f"{self.username}:{self.password}@"
        url = f"mongodb://{credentials}{self.host}:{self.port}"
        return pymongo.MongoClient(url)

    def get_collection(self, collection_name: str):
        return PymongoWrapper.client[self.name][collection_name]


class InventoryAlertWrapper:
    def __init__(self, environment_wrapper) -> None:
        self.alert_url = environment_wrapper.get_var("INVENTORY_ALERT_URL")

    def send_alert(self, alert: dict) -> Any:
        try:
            return requests.post(self.alert_url, json=alert)
        except requests.exceptions.ConnectionError:
            return None