from datetime import datetime


class InventoryItem:
    def __init__(self):
        self.id = None
        self.author = None
        self.title = None
        self.price = None
        self.quantity = None
        self.alert = None
        self.created_at = None

    @staticmethod
    def from_request(attributes: dict):
        item = InventoryItem()
        item.author = attributes["author"]
        item.title = attributes["title"]
        item.price = attributes["price"]
        item.quantity = attributes["quantity"]
        item.alert = None
        item.created_at = datetime.utcnow()
        return item
    
    def assign_request(self, attributes: dict):
        self.author = attributes["author"]
        self.title = attributes["title"]
        self.price = attributes["price"]
        self.quantity = attributes["quantity"]


class InventoryAlert:
    def __init__(self):
        self.id = None
        self.inventory_item_id = None
        self.quantity = None
        self.created_at = None

    @staticmethod
    def from_request(attributes: dict):
        alert = InventoryAlert()
        alert.quantity = attributes["quantity"]
        alert.created_at = datetime.utcnow()
        return alert
