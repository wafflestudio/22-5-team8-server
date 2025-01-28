from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Annotated
from watchapedia.app.auth.service import AuthService
from watchapedia.app.user.dto.responses import UserSigninResponse
from watchapedia.auth.settings import OAUTH_SETTINGS, JWT_SETTINGS


auth_router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"

@auth_router.get("/google")
async def sigin_google():
    # scope : openid, profile, email
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?client_id={OAUTH_SETTINGS.google_client_id}&redirect_uri={OAUTH_SETTINGS.google_client_id}&response_type=code&scope=openid%20profile%20email")

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

@auth_router.get("/kakao")
async def signin_kakao():
    return RedirectResponse(url=f"{KAKAO_AUTH_URL}?client_id={OAUTH_SETTINGS.kakao_client_id}&redirect_uri={OAUTH_SETTINGS.kakao_redirect_uri}&response_type=code&scope=profile_nickname profile_image")

@auth_router.get("/kakao/callback")
async def signin_kakao_callback(
    response: JSONResponse,
    code: str,
    auth_service: Annotated[AuthService, Depends()]
    ):
    user_info = await auth_service.get_kakao_user_info(code)
    print(user_info)
    username = user_info["kakao_account"]["profile"]["nickname"]
    profile_url = user_info["kakao_account"]["profile"]["thumbnail_image_url"]
    access_token, refresh_token, user_id = auth_service.signin(username=username, login_id=username, profile_url=profile_url) # 카카오는 login_id으로 username을 사용

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=JWT_SETTINGS.refresh_token_expires_hours*3600,
        samesite="lax",
    )
    
    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token, user_id=user_id)