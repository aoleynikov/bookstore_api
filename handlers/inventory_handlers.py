from .common import BaseHandler


class GetInventoryListHandler(BaseHandler):
    def __init__(self, validator, presenter, inventory_service):
        super().__init__(validator, presenter)
        self.inventory_service = inventory_service
        self.success_code = 200

    def execute(self, request, **kwargs):
        return self.inventory_service.get_all()
    

class CreateInventoryItemHandler(BaseHandler):
    def __init__(self, validator, presenter, inventory_service):
        super().__init__(validator, presenter)
        self.inventory_service = inventory_service
        self.success_code = 201

    def execute(self, request, **kwargs):
        body = request.json

        item = self.inventory_service.create(body)

        return item
    

class UpdateInventoryItemHandler(BaseHandler):
    def __init__(self, validator, presenter, inventory_service):
        super().__init__(validator, presenter)
        self.inventory_service = inventory_service
        self.success_code = 200

    def execute(self, request, **kwargs):
        body = request.json
 
        item_id = kwargs.get("item_id")
        item = self.inventory_service.update(item_id, body)

        return item
    

class DeleteInventoryItemHandler(BaseHandler):
    def __init__(self, validator, presenter, inventory_service):
        super().__init__(validator, presenter)
        self.inventory_service = inventory_service
        self.success_code = 204

    def execute(self, request, **kwargs):
        item_id = kwargs.get("item_id")
        self.inventory_service.delete(item_id)

        return None


class CreateInventoryAlertHandler(BaseHandler):
    def __init__(self, validator, presenter, inventory_alerts_service):
        super().__init__(validator, presenter)
        self.inventory_alerts_service = inventory_alerts_service
        self.success_code = 201

    def execute(self, request, **kwargs):
        body = request.json

        item_id = kwargs.get("item_id")
        alert = self.inventory_alerts_service.create_alert(item_id, body)

        return alert