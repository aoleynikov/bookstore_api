from models.inventory import InventoryItem, InventoryAlert
from exceptions import NotFoundException


class InventoryService:
    def __init__(self, inventory_repository, update_inentory_observer):
        self.inventory_repository = inventory_repository
        self.update_inentory_observer = update_inentory_observer

    def create(self, attrs: dict):
        item = InventoryItem.from_request(attrs)
        item.id = self.inventory_repository.create(item)
        return item
    
    def update(self, item_id, attrs: dict):
        item = self.inventory_repository.find_by_id(item_id)

        if not item:
            raise NotFoundException()
        self.__fire_update_event(item, attrs.get("quantity"))
        item.assign_request(attrs)
        self.inventory_repository.update(item)
        return item
    
    def delete(self, item_id):
        item = self.inventory_repository.find_by_id(item_id)
        if not item:
            raise NotFoundException()
        self.inventory_repository.delete(item)

    def get_all(self):
        return self.inventory_repository.get_list()
    
    def create_alert(self, item_id, attrs: dict):
        item = self.inventory_repository.find_by_id(item_id)
        if not item:
            raise NotFoundException()
        item.alert = InventoryAlert.from_request(attrs)
        self.__fire_update_event(item, item.quantity)
        self.inventory_repository.update(item)
        return item.alert
    
    def __fire_update_event(self, item, new_count):
        if not self.update_inentory_observer:
            return
        
        self.update_inentory_observer.fire(item, new_count)


class InventoryUpdateObserver:
    def __init__(self, inventory_repository, notification_service, inventory_item_presenter):
        self.inventory_repository = inventory_repository
        self.notification_service = notification_service
        self.inventory_item_presenter = inventory_item_presenter

    def fire(self, item, new_count):
        if not item.alert:
            return
        
        alert_payload = {}
        if item.alert.quantity <= new_count:
            return
        
        alert_payload["most_recent"] = self.inventory_item_presenter.present(item)

        other_violations = self.inventory_repository.get_alert_violations()
        alert_payload["other"] = [self.inventory_item_presenter.present(item) for item in other_violations]

        self.notification_service.send_alert(alert_payload)