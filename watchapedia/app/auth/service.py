from fastapi import Depends
import requests
from watchapedia.app.user.repository import UserRepository
from watchapedia.common.errors import InvalidCredentialsError, InvalidTokenError, BlockedTokenError
from watchapedia.app.auth.utils import verify_password, create_access_token, create_refresh_token, decode_token
from watchapedia.app.auth.settings import JWT_SETTINGS, OAUTH_SETTINGS
from watchapedia.app.auth.errors import GoogleOAuthError
from watchapedia.app.user.errors import UserAlreadyExistsError
from datetime import datetime
from uuid import uuid4
from typing import Annotated

class AuthService():
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
    
    async def social_signin(self, code: str) -> tuple[str, str]:
        GOOGLE_CALLBACK_URI = "https://d2vsqxcvld4zf7.cloudfront.net/sign_in/naver/callback"
        try:
            token_url = f"https://oauth2.googleapis.com/token?client_id={OAUTH_SETTINGS.client_id}&client_secret={OAUTH_SETTINGS.client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}"
            token_response = await requests.post(token_url)
            if token_response.status_code != 200:
                raise GoogleOAuthError()
            # google에 회원 정보 요청
            access_token = token_response.json()['access_token']
            user_info = f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}"
            user_response = await requests.get(user_info)
            if user_response.status_code != 200:
                raise GoogleOAuthError()
        except:
            raise GoogleOAuthError()
        
        email = user_response.json()['email']
        username = email.split('@')[0]

        if self.user_repository.get_user_by_login_id(email) is None:
            self.add_user(username, email, None)
            return None, None
        else:
            return self.issue_token(email)

    
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