from fastapi import APIRouter, Depends, Cookie, Request
from fastapi.responses import JSONResponse
from watchapedia.app.user.dto.requests import UserSignupRequest, UserSigninRequest, UserUpdateRequest
from watchapedia.app.user.dto.responses import UserSigninResponse, MyProfileResponse, UserProfileResponse
from watchapedia.app.user.models import User
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
from watchapedia.app.user.service import UserService
from watchapedia.app.user.errors import InvalidTokenError, UserNotFoundError
from watchapedia.common.errors import InvalidCredentialsError
from watchapedia.auth.settings import JWT_SETTINGS
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
                description="access_token을 헤더에 담아 요청하면 내 정보(유저 이름, 로그인 id, 프로필 url)를 반환합니다.",
                response_model=MyProfileResponse
                )
def me(
    user: User = Depends(login_with_header)
):
    return MyProfileResponse(username=user.username, login_id=user.login_id, profile_url=user.profile_url)

@user_router.patch('/me', status_code=200, summary="내 정보 수정", description="access_token을 헤더에 담아 요청하면 내 정보를 수정하고 성공 시 'Success'를 반환합니다.")
def update_me(
    user: Annotated[User, Depends(login_with_header)],
    update_request: UserUpdateRequest,
    user_service: Annotated[UserService, Depends()],
):
    user_service.update_user(user.id, username= update_request.username, login_password=update_request.login_password, profile_url=update_request.profile_url, status_message=update_request.status_message)
    return "Success"

@user_router.post('/follow/{follow_user_id}', status_code=201, summary="팔로우", description="user_id를 받아 해당 유저를 팔로우하고 성공 시 'Success'를 반환합니다.")
def follow(
    follow_user_id: int,
    user_service: Annotated[UserService, Depends()],
    user: User = Depends(login_with_header),
):
    user_service.follow(user.id, follow_user_id)
    return "Success"

@user_router.delete('/follow/{follow_user_id}', status_code=200, summary="언팔로우", description="user_id를 받아 해당 유저를 언팔로우하고 성공 시 'Success'를 반환합니다.")
def unfollow(
    follow_user_id: int,
    user_service: Annotated[UserService, Depends()],
    user: User = Depends(login_with_header),
):
    user_service.unfollow(user.id, follow_user_id)
    return "Success"

@user_router.get('/followings/{user_id}', status_code=200, summary="팔로잉 목록", description="user_id를 받아 해당 유저가 팔로우하는 유저들의 목록을 반환합니다.")
def followings(
    user_id: int,
    user_service: Annotated[UserService, Depends()],
) -> list[MyProfileResponse]:
    return user_service.get_followings(user_id)

@user_router.get('/followers/{user_id}', status_code=200, summary="팔로워 목록", description="user_id를 받아 해당 유저를 팔로우하는 유저들의 목록을 반환합니다.")
def followers(
    user_id: int,
    user_service: Annotated[UserService, Depends()],
):
    return user_service.get_followers(user_id)

@user_router.get('/profile/{user_id}', status_code=200, summary="프로필 조회", description="user_id를 받아 해당 유저의 프로필 정보를 반환합니다.")
def profile(
    user_id: int,
    user_service: Annotated[UserService, Depends()],
):
    user = user_service.get_user_by_user_id(user_id)
    if user is None:
        raise UserNotFoundError()
    following_count = user_service.get_followings_count(user_id)    
    follwer_count = user_service.get_followers_count(user_id)
    review_count = user_service.get_reviews_count(user_id)
    comment_count = user_service.get_comments_count(user_id)
    collection_count = user_service.get_collections_count(user_id)
    return UserProfileResponse.from_user(user, following_count, follwer_count, review_count, comment_count, collection_count)

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