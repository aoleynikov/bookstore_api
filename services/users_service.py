from models.user import User

from exceptions import NotFoundException, InvalidRequestException, UnauthorizedException


class UsersService:
    def __init__(
        self,
        users_repository,
        password_service,
    ) -> None:
        self.users_repository = users_repository
        self.password_service = password_service

    def create(self, attributes: dict, password_length=8):
        password = attributes.get("password")
        if not password:
            password = self.password_service.generate_password(password_length)
        attributes["password_hash"] = self.password_service.create_hash(password)
        attributes["email"] = attributes["email"].lower()

        user = User.from_request(attributes)
        user.id = self.users_repository.create(user)
        
        return user

    def delete(self, user_id: str) -> None:
        user = self.__find_user(user_id)
        self.users_repository.delete(user)

    def update(self, user_id: str, attributes: dict) -> User:
        user = self.__find_user(user_id)

        user.assign_request(attributes)

        self.users_repository.update(user)
        return user

    def find(self, user_id: str) -> User:
        user = self.__find_user(user_id)
        return user

    def __find_user(self, user_id) -> User:
        user = self.users_repository.find_by_id(user_id)
        if not user:
            raise NotFoundException()
        return user
