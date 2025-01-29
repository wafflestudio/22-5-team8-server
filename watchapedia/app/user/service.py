from typing import Annotated
from watchapedia.app.user.repository import UserRepository
from fastapi import Depends
from watchapedia.common.errors import InvalidCredentialsError, InvalidRangeError, InvalidTokenError, BlockedTokenError
from watchapedia.app.user.errors import UserAlreadyExistsError, UserNotFoundError, UserAlreadyFollowingError, UserAlreadyNotFollowingError, CANNOT_FOLLOW_MYSELF_Error, CANNOT_BLOCK_MYSELF_Error, UserBlockedError, UserNotBlockedError
from watchapedia.app.user.dto.responses import MyProfileResponse, UserResponse
from watchapedia.auth.utils import verify_password
from watchapedia.app.user.models import User
from watchapedia.auth.utils import create_access_token, create_refresh_token, decode_token
from watchapedia.auth.settings import JWT_SETTINGS
from datetime import datetime
from uuid import uuid4

class UserService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends()]) -> None:
        self.user_repository = user_repository

    def add_user(self, username: str, login_id: str, login_password: str) -> None:
        self.raise_if_user_exists(username, login_id)
        self.user_repository.add_user(username=username, login_id=login_id, login_password=login_password)

    def signin(self, login_id: str, login_password: str) -> tuple[str, str]:
        user = self.get_user_by_login_id(login_id)
        if user is None or verify_password(login_password, user.hashed_pwd) is False:
            raise InvalidCredentialsError()
        # access token은 10분, refresh token은 24시간 유효한 토큰 생성
        access_token, refresh_token = self.issue_token(login_id)
        return access_token, refresh_token, user.id
    
    def follow(self, follower_id: int, following_id: int) -> None:
        if self.get_user_by_user_id(following_id) is None:
            raise UserNotFoundError()
        if follower_id == following_id:
            raise CANNOT_FOLLOW_MYSELF_Error()
        if self.user_repository.is_following(follower_id, following_id):
            raise UserAlreadyFollowingError()
        self.user_repository.follow(follower_id, following_id)

    def unfollow(self, follower_id: int, following_id: int) -> None:
        if self.get_user_by_user_id(following_id) is None:
            raise UserNotFoundError()
        if follower_id == following_id:
            raise CANNOT_FOLLOW_MYSELF_Error()
        if not self.user_repository.is_following(follower_id, following_id):
            raise UserAlreadyNotFollowingError()
        self.user_repository.unfollow(follower_id, following_id)
    
    def get_followings(self, user_id: int, begin: int | None, end: int | None) -> list[MyProfileResponse]:
        if self.get_user_by_user_id(user_id) is None:
            raise UserNotFoundError()
        users= self.user_repository.get_followings(user_id)
        return self._process_range([self._process_user_response(user) for user in users], begin, end)
    
    def get_followers(self, user_id: int, begin: int | None, end: int | None) -> list[MyProfileResponse]:
        if self.get_user_by_user_id(user_id) is None:
            raise UserNotFoundError()
        users = self.user_repository.get_followers(user_id)
        return self._process_range([self._process_user_response(user) for user in users], begin, end)
    
    def get_followings_count(self, user_id: int) -> int:
        return self.user_repository.get_followings_count(user_id)
    
    def get_followers_count(self, user_id: int) -> int:
        return self.user_repository.get_followers_count(user_id)
    
    def get_reviews_count(self, user_id: int) -> int:
        return self.user_repository.get_reviews_count(user_id)
    
    def get_comments_count(self, user_id: int) -> int:
        return self.user_repository.get_comments_count(user_id)
    
    def get_collections_count(self, user_id: int) -> int:
        return self.user_repository.get_collections_count(user_id)
    
    def update_user(self, user_id:int, username: str | None, login_password: str | None, profile_url: str | None, status_message: str | None) -> None:
        self.user_repository.update_user(user_id, username, login_password, profile_url, status_message)

    def raise_if_user_exists(self, username: str, login_id: str) -> None:
        if self.user_repository.get_user(username, login_id) is not None:
            raise UserAlreadyExistsError()
        
    def get_user_by_login_id(self, login_id: str) -> User | None:
        return self.user_repository.get_user_by_login_id(login_id)
    
    def get_user_by_user_id(self, user_id: int) -> User | None:
        return self.user_repository.get_user_by_user_id(user_id)
    
    def get_user_by_username(self, username: str) -> User | None:
        return self.user_repository.get_user_by_username(username)
    
    def search_user_list(self, username: str) -> list[UserResponse] | None:
        users = self.user_repository.search_user_list(username)
        return [UserResponse(
                id=user.id) for user in users]
    
    def block_user(self, blocker_id: int, blocked_id: int) -> None:
        if self.get_user_by_user_id(blocked_id) is None:
            raise UserNotFoundError()
        if blocker_id == blocked_id:
            raise CANNOT_BLOCK_MYSELF_Error()
        if self.user_repository.is_blocked(blocker_id, blocked_id):
            raise UserBlockedError()
        self.user_repository.block_user(blocker_id, blocked_id)

    def unblock_user(self, blocker_id: int, blocked_id: int) -> None:
        if self.get_user_by_user_id(blocked_id) is None:
            raise UserNotFoundError()
        if blocker_id == blocked_id:
            raise CANNOT_BLOCK_MYSELF_Error()
        if not self.user_repository.is_blocked(blocker_id, blocked_id):
            raise UserNotBlockedError()
        self.user_repository.unblock_user(blocker_id, blocked_id)
        
    def get_blocked_users(self, user_id: int) -> list[int]:
        if self.get_user_by_user_id(user_id) is None:
            raise UserNotFoundError()
        return self.user_repository.get_blocked_users(user_id)

    def validate_access_token(self, token: str) -> dict:
        payload = decode_token(token)
        if payload['typ'] != 'access':
            raise InvalidTokenError()
        return payload['sub']
    
    def validate_refresh_token(self, token: str) -> dict:
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
    
    def block_refresh_token(self, token_id: str, expired_at: datetime) -> None:
        self.user_repository.block_token(token_id, expired_at)
    
    def _process_user_response(self, user: User) -> MyProfileResponse:
        return MyProfileResponse(
            username=user.username,
            login_id=user.login_id,
            profile_url=user.profile_url
            )
    
    def _process_range(self, response_list, begin: int | None, end: int | None) -> list[MyProfileResponse]:
        if begin is None :
            begin = 0
        if end is None or end > len(response_list) :
            end = len(response_list)
        if begin > len(response_list) :
            begin = len(response_list)
        if begin < 0 or begin > end :
            raise InvalidRangeError()
        return response_list[begin : end]
