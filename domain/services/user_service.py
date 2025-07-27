from domain.models.user import User


class UserService:

    @staticmethod
    def convert_dict_to_user(user_dict: dict) -> User:
        return User(**user_dict)
