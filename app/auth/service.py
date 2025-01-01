from fastapi import Depends
from app.user.repository import UserRepository
from common.errors import InvalidCredentialsError, InvalidTokenError, BlockedTokenError
from app.auth.utils import verify_password, create_access_token, create_refresh_token, decode_token
from app.user.errors import UserAlreadyExistsError
from app.auth.settings import JWT_SETTINGS
from datetime import datetime
from uuid import uuid4
from typing import Annotated

class AuthService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends()]) -> None:
        self.user_repository = user_repository

    def add_user(self, username: str, login_id: str, login_password: str) -> None:
            self.raise_if_user_exists(username, login_id)
            self.user_repository.add_user(username=username, login_id=login_id, login_password=login_password)

    def signin(self, login_id: str, login_password: str) -> tuple[str, str]:
        user = self.user_repository.get_user_by_login_id(login_id)
        if user is None or verify_password(login_password, user.hashed_pwd) is False:
            raise InvalidCredentialsError()
            
        # access token은 10분, refresh token은 24시간 유효한 토큰 생성
        return self.issue_token(login_id)
    
    def validate_access_token(self, token: str) -> str:
        payload = decode_token(token)
        if payload['typ'] != 'access':
            raise InvalidTokenError()
        return payload['sub']
    
    def validate_refresh_token(self, token: str) -> str:
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
    
    def raise_if_user_exists(self, username: str, login_id: str) -> None:
        if self.user_repository.get_user(username, login_id) is not None:
            raise UserAlreadyExistsError()
    
    def block_refresh_token(self, token_id: str, expired_at: datetime) -> None:
        self.user_repository.block_token(token_id, expired_at)