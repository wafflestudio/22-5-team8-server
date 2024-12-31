from typing import Annotated
from app.user.repository import UserRepository
from fastapi import Depends
from common.errors import InvalidCredentialsError, InvalidTokenError, BlockedTokenError
from app.user.errors import UserAlreadyExistsError
from auth.utils import verify_password
from app.user.models import User
from auth.utils import create_access_token, create_refresh_token, decode_token
from auth.settings import JWT_SETTINGS
from datetime import datetime
from uuid import uuid4

class UserService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends()]) -> None:
        self.user_repository = user_repository

    def add_user(self, username: str, login_id: str, login_password: str) -> None:
        self.raise_if_user_exists(username, login_id)
        self.user_repository.add_user(username=username, login_id=login_id, login_password=login_password)

    def signin(self, login_id: str, login_password: str) -> tuple[str, str]:
        user = self.get_user_by_login_id(login_id)
        if user is None or verify_password(login_password, user.hashed_pwd) is False:
            raise InvalidCredentialsError()
        
        # access token은 10분, refresh token은 24시간 유효한 토큰 생성
        return self.issue_token(login_id)
    
    def update_user(self, user_id:int, username: str | None, login_password: str | None) -> None:
        self.user_repository.update_user(user_id, username, login_password)

    def raise_if_user_exists(self, username: str, login_id: str) -> None:
        if self.user_repository.get_user(username, login_id) is not None:
            raise UserAlreadyExistsError()
        
    def get_user_by_login_id(self, login_id: str) -> User | None:
        return self.user_repository.get_user_by_login_id(login_id)
    
    def get_user_by_user_id(self, user_id: int) -> User | None:
        return self.user_repository.get_user_by_user_id(user_id)
    
    def get_user_by_username(self, username: str) -> User | None:
        return self.user_repository.get_user_by_username(username)
    
    def validate_access_token(self, token: str) -> dict:
        payload = decode_token(token)
        if payload['typ'] != 'access':
            raise InvalidTokenError()
        return payload['sub']
    
    def validate_refresh_token(self, token: str) -> dict:
        payload = decode_token(token)
        if payload['typ'] != 'refresh':
            raise InvalidTokenError()
        if self.user_repository.is_token_blocked(token):
            raise BlockedTokenError()
        return payload['sub']
    
    def issue_token(self, login_id: str) -> tuple[str, str]:
        return create_access_token({'sub': login_id}, JWT_SETTINGS.access_token_expires_minutes), \
    create_refresh_token({'sub': login_id, 'jti': uuid4().hex}, JWT_SETTINGS.refresh_token_expires_hours)

    def reissue_token(self, refresh_token: str) -> tuple[str, str]:
        login_id = self.validate_refresh_token(refresh_token)
        self.user_repository.block_token(refresh_token, datetime.now())

        return self.issue_token(login_id)
    
    def block_refresh_token(self, token_id: str, expired_at: datetime) -> None:
        self.user_repository.block_token(token_id, expired_at)