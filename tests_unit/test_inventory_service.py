from unittest.mock import Mock, call
from services import InventoryService, InventoryUpdateObserver

class TestInventoryService:
    def test_create_alert(self):
        inventory_repository = Mock()
        inventory_repository.find_by_id.return_value = Mock(alert=None)
        update_inventory_observer = Mock()

        service = InventoryService(inventory_repository, update_inventory_observer)

        service.create_alert(1, {'quantity': 10})

        update_inventory_observer.fire.assert_called_once()

class TestInventoryUpdateObserver:
    def test_fire_makes_call(self):
        inventory_repository = Mock()
        inventory_repository.get_alert_violations.return_value = []
        notification_service = Mock()
        inventory_item_presenter = Mock()
        inventory_item_presenter.present.return_value = {}

        observer = InventoryUpdateObserver(inventory_repository, notification_service, inventory_item_presenter)

        item = Mock(alert=Mock(quantity=10))
        observer.fire(item, 5)

        notification_service.send_alert.assert_called_once_with({"most_recent": {}, "other": []})

    def test_fire_makes_no_call(self):
        inventory_repository = Mock()
        inventory_repository.get_alert_violations.return_value = []
        notification_service = Mock()
        inventory_item_presenter = Mock()
        inventory_item_presenter.present.return_value = {}

        observer = InventoryUpdateObserver(inventory_repository, notification_service, inventory_item_presenter)

        item = Mock(alert=Mock(quantity=10))
        observer.fire(item, 15)

        notification_service.send_alert.assert_not_called()
