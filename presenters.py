class BasePresenter:
    def present_time(self, datetime):
        if datetime:
            return datetime.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def present_date(self, datetime):
        if datetime:
            return datetime.strftime("%Y-%m-%d")
        return None


class ListPresenter(BasePresenter):
    def __init__(self, item_presenter):
        self.item_presenter = item_presenter

    def present(self, items):
        return [self.item_presenter.present(item) for item in items]


class UserPresenter(BasePresenter):
    def present(self, user):
        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "created_at": self.present_time_iso(user.created_at),
        }


class TokenPairPresenter(BasePresenter):
    def present(self, item):
        return {"access_token": item.access, "refresh_token": item.refresh}


class InventoryItemPresenter(BasePresenter):
    def __init__(self, alert_presenter):
        self.alert_presenter = alert_presenter

    def present(self, item):
        return {
            "id": str(item.id),
            "author": item.author,
            "title": item.title,
            "price": item.price,
            "quantity": item.quantity,
            "alert": self.alert_presenter.present(item.alert),
            "created_at": self.present_time(item.created_at),
        }


class InventoryAlertPresenter(BasePresenter):
    def present(self, item):
        if not item:
            return None
        return {
            "quantity": item.quantity,
        }