from pydantic import BaseModel

class MyProfileResponse(BaseModel):
    username: str
    login_id: str
    profile_url: str | None = None

    @staticmethod
    def from_user(user) -> 'MyProfileResponse':
        return MyProfileResponse(
            username=user.username, 
            login_id=user.login_id,
            )

class UserProfileResponse(BaseModel):
    username: str
    login_id: str
    profile_url: str | None = None
    status_message: str | None = None
    following_count: int | None = None
    follower_count: int | None = None
    review_count: int | None = None
    collection_count: int | None = None

    @staticmethod
    def from_user(user, following_count, follower_count, review_count, collection_count) -> 'UserProfileResponse':
        return UserProfileResponse(
            username=user.username, 
            login_id=user.login_id,
            profile_url=user.profile_url,
            status_message=user.status_message,
            following_count=following_count,
            follower_count=follower_count,
            review_count=review_count,
            collection_count=collection_count
        )
class UserSigninResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int | None = None


class UserResponse(BaseModel):
    id: int

class BlockedUsersResponse(BaseModel):
    id: list[int]

    @staticmethod
    def from_user(users: list[int]) -> 'BlockedUsersResponse':
        return BlockedUsersResponse(
            id=users
        )