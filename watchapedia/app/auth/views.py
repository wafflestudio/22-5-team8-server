from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Annotated
from watchapedia.app.auth.service import AuthService
from watchapedia.app.user.dto.responses import UserSigninResponse
from watchapedia.auth.settings import OAUTH_SETTINGS, JWT_SETTINGS


auth_router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"

@auth_router.get("/google")
async def sigin_google():
    # scope : openid, profile, email
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?client_id={OAUTH_SETTINGS.client_id}&redirect_uri={OAUTH_SETTINGS.redirect_uri}&response_type=code&scope=openid%20profile%20email")

@auth_router.get("/google/callback")
async def signin_google_callback(
    response: JSONResponse,
    code: str, 
    auth_service: Annotated[AuthService, Depends()]
    ):
    user_info = await auth_service.get_google_user_info(code)
    username = user_info["email"].split("@")[0]
    profile_url = user_info.get("picture")
    access_token, refresh_token, user_id = auth_service.signin(username=username, login_id=user_info["email"], profile_url=profile_url)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=JWT_SETTINGS.refresh_token_expires_hours*3600,
        samesite="lax",
    )
    
    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token, user_id=user_id)