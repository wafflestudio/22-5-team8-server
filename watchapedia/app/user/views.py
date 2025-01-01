from fastapi import APIRouter, Depends
from watchapedia.app.user.dto.requests import UserUpdateRequest
from watchapedia.app.user.dto.responses import MyProfileResponse
from watchapedia.app.user.models import User
from typing import Annotated
from watchapedia.app.user.service import UserService
from watchapedia.app.auth.views import login_with_header

user_router = APIRouter()

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