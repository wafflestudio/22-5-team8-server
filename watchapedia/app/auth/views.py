from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
from watchapedia.common.errors import InvalidTokenError
from watchapedia.app.auth.service import AuthService
from watchapedia.app.user.service import UserService
from watchapedia.app.user.models import User
from watchapedia.app.auth.settings import JWT_SETTINGS
from fastapi.responses import JSONResponse
from watchapedia.app.auth.dto.requests import UserSignupRequest, UserSigninRequest, SocialLogin
from watchapedia.app.auth.dto.responses import UserSigninResponse
from datetime import datetime
from watchapedia.app.auth.errors import InvalidLoginProviderError
from enum import Enum

security = HTTPBearer()

auth_router = APIRouter()

class PROVIDER_ENUM(Enum):
    GOOGLE = ('google')

    def __init__(self, title):
        self.title = title

    @classmethod
    def from_str(cls, name: str):
        for enum in cls:
            if enum.value == name:
                return enum


def login_with_header(
    auth_service: Annotated[AuthService, Depends()],
    user_service: Annotated[UserService, Depends()],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    token = credentials.credentials
    login_id = auth_service.validate_access_token(token)
    user = user_service.get_user_by_login_id(login_id)
    if not user:
        raise InvalidTokenError()
    return user

@auth_router.post('/signup', 
                status_code=201, 
                summary="회원가입", 
                description="username, login_id, login_password를 받아 회원가입을 진행하고 성공 시 'Success'를 반환합니다.",
                responses={
                    201: {
                        "description": "회원가입 성공",
                        "content": {
                            "application/json": {
                                "example": "Success"
                            }
                        }
                    }
                }
        )
def signup(
    signup_request: UserSignupRequest,
    auth_service: Annotated[AuthService, Depends()]
):
    auth_service.add_user(signup_request.username, signup_request.login_id, signup_request.login_password)

    return "Success"

@auth_router.post('/signin', 
                  status_code=201, 
                  summary="로그인", 
                  description="login_id와 login_password를 받아 로그인을 진행하고 성공 시 refresh_token을 쿠키에 저장하고 두 토큰의 값을 반환합니다.",
                  response_model=UserSigninResponse
                  )
def signin(
    response: JSONResponse,
    auth_service: Annotated[AuthService, Depends()],
    signin_request: UserSigninRequest,
):
    # 토큰 발급
    access_token, refresh_token = auth_service.signin(signin_request.login_id, signin_request.login_password)

    # refresh_token은 쿠키에 담아서 반환
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=JWT_SETTINGS.refresh_token_expires_hours*3600,
        samesite="lax",
    )
    
    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token)

@auth_router.post("/{provider}/",
                 status_code=201,
                 summary="소셜 로그인",
                 description="소셜 로그인을 진행하고 성공했을 때 이미 회원가입된 유저라면 액세스 토큰과 리프레시 토큰을 반환하고, 회원가입되지 않은 유저라면 회원가입을 진행하고 Success를 반환합니다",)
async def social_signin(
    provider: str,
    form: SocialLogin,
    auth_service: Annotated[AuthService, Depends()],
):
    provider = PROVIDER_ENUM.from_str(provider.lower())
    if not provider:
        raise InvalidLoginProviderError()
    if provider == PROVIDER_ENUM.GOOGLE:
        access_token, refresh_token = await auth_service.social_signin(form.code)
    
    if access_token and refresh_token:
        return UserSigninResponse(access_token=access_token, refresh_token=refresh_token)
    return "Success"

@auth_router.get('/refresh', 
                status_code=200, 
                summary="토큰 갱신", 
                description="refresh_token을 쿠키에서 받아 access_token과 refresh_token을 갱신하고 반환합니다.",
                response_model=UserSigninResponse
                )
def refresh(
    request: Request,
    response: JSONResponse,
    auth_service: Annotated[AuthService, Depends()],
):
    refresh_token = request.cookies.get("refresh_token")
    access_token, refresh_token = auth_service.reissue_token(refresh_token)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=JWT_SETTINGS.refresh_token_expires_hours*3600,
        samesite="lax"
    )
    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token)


@auth_router.get('/logout', 
                status_code=200, 
                summary="로그아웃", 
                description="refresh_token을 쿠키에서 받아 삭제하고 성공 시 'Success'를 반환합니다.",
                responses={
                    200: {
                        "description": "회원가입 성공",
                        "content": {
                            "application/json": {
                                "example": "Success"
                            }
                        }
                    }
                }
                )
def logout(
    request: Request,
    response: JSONResponse,
    auth_service: Annotated[AuthService, Depends()],
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise InvalidTokenError()
    response.delete_cookie(key="refresh_token")
    auth_service.block_refresh_token(refresh_token, datetime.now())
    return "Success"