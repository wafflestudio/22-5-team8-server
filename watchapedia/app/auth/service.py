from fastapi import HTTPException, Depends
from typing import Annotated
import httpx
from watchapedia.app.auth.errors import AuthorizationCodeNotFound
from watchapedia.app.user.service import UserService
from watchapedia.app.user.repository import UserRepository
from watchapedia.auth.settings import OAUTH_SETTINGS

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

class AuthService:
    def __init__(self, 
                 user_service: Annotated[UserService, Depends()],
                 user_repository: Annotated[UserRepository, Depends()],
                 ) -> None:
        self.user_service = user_service
        self.user_repository = user_repository

    async def get_google_user_info(self, code: str):
        if code is None:
            raise AuthorizationCodeNotFound()
        
        data = {
            "code": code,
            "client_id": OAUTH_SETTINGS.client_id,
            "client_secret": OAUTH_SETTINGS.client_secret,
            "redirect_uri": OAUTH_SETTINGS.redirect_uri,
            "grant_type": "authorization_code"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(GOOGLE_TOKEN_URL, data=data)
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to retrieve access token")

            token_data = response.json()
            access_token = token_data["access_token"]

        async with httpx.AsyncClient() as client:
            user_info_response = await client.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
            if user_info_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to retrieve user info")
            
            user_info = user_info_response.json()

        return user_info
    
    def signin(self, username: str, login_id: str, profile_url: str | None):
        user = self.user_repository.get_user_by_login_id(login_id)
        # 사용자가 존재하지 않으면 사용자를 추가
        if user is None:
            self.user_repository.add_user(username=username, login_id=login_id, profile_url=profile_url)
            user = self.user_repository.get_user_by_login_id(login_id)
        access_token, refresh_token = self.user_service.issue_token(login_id)
        return access_token, refresh_token, user.id