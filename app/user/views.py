from fastapi import APIRouter, Depends, Cookie, Request
from fastapi.responses import JSONResponse
from app.user.dto.requests import UserSignupRequest, UserSigninRequest, UserUpdateRequest
from app.user.dto.responses import UserSigninResponse, MyProfileResponse
from app.user.models import User
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
from app.user.service import UserService
from app.user.errors import InvalidTokenError
from auth.settings import JWT_SETTINGS
from datetime import datetime

user_router = APIRouter()
security = HTTPBearer()

def login_with_header(
    user_service: Annotated[UserService, Depends()],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    token = credentials.credentials
    login_id = user_service.validate_access_token(token)
    user = user_service.get_user_by_login_id(login_id)
    if not user:
        raise InvalidTokenError()
    return user

@user_router.post('/signup', 
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
    user_service: Annotated[UserService, Depends()]
):
    user_service.add_user(signup_request.username, signup_request.login_id, signup_request.login_password)

    return "Success"

@user_router.post('/signin', 
                  status_code=201, 
                  summary="로그인", 
                  description="login_id와 login_password를 받아 로그인을 진행하고 성공 시 refresh_token을 쿠키에 저장하고 두 토큰의 값을 반환합니다.",
                  response_model=UserSigninResponse
                  )
def signin(
    response: JSONResponse,
    user_service: Annotated[UserService, Depends()],
    signin_request: UserSigninRequest
):
    # 토큰 발급
    access_token, refresh_token = user_service.signin(signin_request.login_id, signin_request.login_password)

    # refresh_token은 쿠키에 담아서 반환
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=JWT_SETTINGS.refresh_token_expires_hours*3600,
        samesite="lax",
    )
    
    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token)

@user_router.get('/me',
                status_code=200, 
                summary="내 정보", 
                description="access_token을 헤더에 담아 요청하면 내 정보를 반환합니다.",
                response_model=MyProfileResponse
                )
def me(
    user: User = Depends(login_with_header)
):
    return MyProfileResponse(username=user.username, login_id=user.login_id, hashed_pwd=user.hashed_pwd)

@user_router.patch('/me', status_code=200, summary="내 정보 수정", description="access_token을 헤더에 담아 요청하면 내 정보를 수정하고 성공 시 'Success'를 반환합니다.")
def update_me(
    user: Annotated[User, Depends(login_with_header)],
    update_request: UserUpdateRequest,
    user_service: Annotated[UserService, Depends()],
):
    user_service.update_user(user.id, username= update_request.username, login_password=update_request.login_password)
    return "Success"


@user_router.get('/refresh', 
                status_code=200, 
                summary="토큰 갱신", 
                description="refresh_token을 쿠키에서 받아 access_token과 refresh_token을 갱신하고 반환합니다.",
                response_model=UserSigninResponse
                )
def refresh(
    request: Request,
    response: JSONResponse,
    user_service: Annotated[UserService, Depends()],
):
    refresh_token = request.cookies.get("refresh_token")
    access_token, refresh_token = user_service.reissue_token(refresh_token)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=JWT_SETTINGS.refresh_token_expires_hours*3600,
        samesite="lax"
    )
    return UserSigninResponse(access_token=access_token, refresh_token=refresh_token)


@user_router.get('/logout', 
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
    user_service: Annotated[UserService, Depends()],
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise InvalidTokenError()
    response.delete_cookie(key="refresh_token")
    user_service.block_refresh_token(refresh_token, datetime.now())
    return "Success"