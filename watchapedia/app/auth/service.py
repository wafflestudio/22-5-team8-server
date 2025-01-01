from fastapi import Depends, Request
from watchapedia.app.user.repository import UserRepository
from watchapedia.common.errors import InvalidCredentialsError, InvalidTokenError, BlockedTokenError
from watchapedia.app.auth.utils import verify_password, create_access_token, create_refresh_token, decode_token
from watchapedia.app.auth.settings import JWT_SETTINGS
from watchapedia.app.user.errors import UserAlreadyExistsError
from watchapedia.app.auth.oauth import oauth
from datetime import datetime
from uuid import uuid4
from typing import Annotated

class AuthService():
    def __init__(self, user_repository: Annotated[UserRepository, Depends()]) -> None:
        self.user_repository = user_repository

    def add_user(self, username: str, login_id: str, login_password: str) -> None:
            self.raise_if_user_exists(username, login_id)
            self.user_repository.add_user(username=username, login_id=login_id, login_password=login_password)

    def signin(self, login_id: str, login_password: str | None) -> tuple[str, str]:
        user = self.user_repository.get_user_by_login_id(login_id)
        if login_password is not None:
            if user is None or verify_password(login_password, user.hashed_pwd) is False:
                raise InvalidCredentialsError()
            
        # access token은 10분, refresh token은 24시간 유효한 토큰 생성
        return self.issue_token(login_id)
    
    async def social_signin(self, request: Request,provider: str) -> tuple[str, str]:
        redirect_uri = f'http://127.0.0.1:8000/api/auth/{provider}/callback' # redirect uri는 이후에 변경, 현재는 테스트용
        return await oauth.create_client(provider).authorize_redirect(request, redirect_uri) # 인증 서버로 이동, 인증 서버에서 토큰 발급 후 콜백 주소로 리다이렉트
    
    async def social_signin_callback(self, request: Request,provider: str) -> tuple[str, str]:
        token = await oauth.create_client(provider).authorize_access_token(request) # 인증 서버로부터 토큰 발급
        print(token)
        # 토큰을 통해 사용자 정보 가져오기
        if provider == 'google':
            userinfo = token['userinfo']
        email = userinfo['email'] # 이메일을 login_id로 사용
        username = userinfo['email'].split('@')[0] # username은 이메일 주소에서 @ 앞부분
        if self.user_repository.get_user_by_login_id(email) is None: # 이미 가입된 사용자인지 확인
            self.user_repository.add_user(username=username, login_id=email, login_password=None) # 가입되지 않은 사용자라면 가입, 소셜 로그인은 비밀번호가 없음
            return None, None
        else:
            return self.signin(email, None)

    
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