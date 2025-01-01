from typing import Annotated
from watchapedia.app.user.repository import UserRepository
from fastapi import Depends

class UserService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends()]) -> None:
        self.user_repository = user_repository
    
    def update_user(self, user_id:int, username: str | None, login_password: str | None) -> None:
        self.user_repository.update_user(user_id, username, login_password)
    
    def get_user_by_login_id(self, login_id: str) -> dict:
        return self.user_repository.get_user_by_login_id(login_id)