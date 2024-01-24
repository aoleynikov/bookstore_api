import os

from handlers.common import RequestValidator, AuthDecorator, Auth
from handlers.user_handlers import RegisterHandler
from handlers.auth_handlers import LoginHandler, RefreshHandler, LogoutHandler
from handlers.inventory_handlers import (
    GetInventoryListHandler, 
    CreateInventoryItemHandler, 
    UpdateInventoryItemHandler, 
    DeleteInventoryItemHandler,
    CreateInventoryAlertHandler,
)
from presenters import ListPresenter, TokenPairPresenter, InventoryItemPresenter, InventoryAlertPresenter
from services import (
    AuthService,
    PasswordService,
    TokensService,
    UsersService,
    InventoryService,
    InventoryUpdateObserver
)
from validators.common import (
    PresenceValidator,
    EmailRegexValidator,
    LengthValidator,
    IntegerValidator,
    PositiveValidator,
)
from validators.user_validators import (
    PasswordsMatchValidator,
    EmailUniqueValidator,
)
from repositories import (
    UsersRepository,
    MongoColumnFactory,
    TokensRepository,
    InventoryRepository,
)
from dependencies import PymongoWrapper, EnvironmentWrapper, InventoryAlertWrapper
from mongo_translators import (
    UserTranslator,
    TokenPairTranslator,
    PasswordResetRequestTranslator,
    ProfileTranslator,
    InventoryItemTranslator,
    InventoryAlertTranslator,
)

columns = MongoColumnFactory()


class Structure:
    env = EnvironmentWrapper()
    db = PymongoWrapper(env)
    notificaiton_service = InventoryAlertWrapper(env)

    @property
    def register_handler(self):
        return RegisterHandler(self.token_pair_presenter, self.register_validator)

    @property
    def token_pair_presenter(self):
        return TokenPairPresenter()

    @property
    def register_validator(self):
        return RequestValidator(
            [
                PresenceValidator("email"),
                EmailRegexValidator("email"),
                PresenceValidator("password"),
                LengthValidator("password", min_length=8, max_length=32),
                PasswordsMatchValidator("password", "password_confirmation"),
                EmailUniqueValidator("email", self.users_repository),
            ]
        )

    @property
    def token_pair_translator(self):
        return TokenPairTranslator()

    @property
    def password_reset_request_translator(self):
        return PasswordResetRequestTranslator()

    @property
    def profile_translator(self):
        return ProfileTranslator()

    @property
    def user_translator(self):
        return UserTranslator(
            self.token_pair_translator,
            self.password_reset_request_translator,
            self.profile_translator,
        )

    @property
    def users_repository(self):
        return UsersRepository(
            Structure.db.get_collection("users"),
            self.user_translator,
            indicies=[columns.ascending("email")],
        )

    @property
    def password_service(self):
        return PasswordService()

    @property
    def tokens_service(self):
        return TokensService(self.env)

    @property
    def logout_token_repository(self):
        return TokensRepository(
            Structure.db.get_collection("logout_tokens"),
            self.token_pair_translator,
            [columns.ascending("access_token"), columns.ascending("refresh_token")],
        )

    @property
    def auth_service(self):
        return AuthService(
            self.users_repository,
            self.logout_token_repository,
            self.password_service,
            self.tokens_service,
        )

    @property
    def users_service(self):
        return UsersService(
            self.users_repository,
            self.password_service,
        )

    @property
    def register_handler(self):
        return RegisterHandler(
            self.register_validator,
            self.token_pair_presenter,
            self.users_service,
            self.auth_service,
        )

    @property
    def login_validator(self):
        return RequestValidator(
            [PresenceValidator("email"), PresenceValidator("password")]
        )

    @property
    def login_handler(self):
        return LoginHandler(
            self.login_validator, self.token_pair_presenter, self.auth_service
        )

    @property
    def refresh_validator(self):
        return RequestValidator([PresenceValidator("refresh_token")])

    @property
    def refresh_handler(self):
        return RefreshHandler(
            self.refresh_validator, self.token_pair_presenter, self.auth_service
        )

    @property
    def logout_handler(self):
        return LogoutHandler(None, self.token_pair_presenter, self.auth_service)
    
    @property
    def inventory_alert_presenter(self):
        return InventoryAlertPresenter()

    @property
    def inventory_item_presenter(self):
        return InventoryItemPresenter(self.inventory_alert_presenter)
    
    @property
    def inventory_list_presenter(self):
        return ListPresenter(self.inventory_item_presenter)
    
    @property
    def inventory_alert_translator(self):
        return InventoryAlertTranslator()
    
    @property
    def inventory_item_translator(self):
        return InventoryItemTranslator(self.inventory_alert_translator)
    
    @property
    def inventory_repository(self):
        return InventoryRepository(
            Structure.db.get_collection("inventory"),
            self.inventory_item_translator,
            indicies=[columns.ascending("name")],
        )
    
    @property
    def update_inventory_observer(self):
        return InventoryUpdateObserver(
            self.inventory_repository, 
            self.notificaiton_service, 
            self.inventory_item_presenter
        )
    
    @property
    def inventory_service(self):
        return InventoryService(self.inventory_repository, self.update_inventory_observer)
    
    @property
    def get_inventory_list_handler(self):
        handler = GetInventoryListHandler(
            None,
            self.inventory_list_presenter,
            self.inventory_service,
        )
        return AuthDecorator(self.auth_service, Auth("*"), handler)
    
    @property
    def inventory_item_validator(self):
        return RequestValidator(
            [
                PresenceValidator("author"),
                PresenceValidator("title"),
                PresenceValidator("price"),
                PresenceValidator("quantity"),
                IntegerValidator("price"),
                IntegerValidator("quantity"),
                PositiveValidator("quantity"),
            ]
        )
    
    @property
    def create_inventory_item_handler(self):
        handler = CreateInventoryItemHandler(
            self.inventory_item_validator,
            self.inventory_item_presenter,
            self.inventory_service,
        )
        return AuthDecorator(self.auth_service, Auth("*"), handler)
    
    @property
    def update_inventory_item_handler(self):
        handler = UpdateInventoryItemHandler(
            self.inventory_item_validator,
            self.inventory_item_presenter,
            self.inventory_service,
        )
        return AuthDecorator(self.auth_service, Auth("*"), handler)
    
    @property
    def delete_inventory_item_handler(self):
        handler = DeleteInventoryItemHandler(
            None,
            self.inventory_item_presenter,
            self.inventory_service,
        )
        return AuthDecorator(self.auth_service, Auth("*"), handler)
    
    @property
    def inventory_alert_validator(self):
        return RequestValidator(
            [
                PresenceValidator("quantity"),
                IntegerValidator("quantity"),
                PositiveValidator("quantity"),
            ]
        )
    
    @property
    def create_inventory_alert_handler(self):
        handler = CreateInventoryAlertHandler(
            self.inventory_alert_validator,
            self.inventory_alert_presenter,
            self.inventory_service,
        )
        return AuthDecorator(self.auth_service, Auth("*"), handler)

structure = Structure()
