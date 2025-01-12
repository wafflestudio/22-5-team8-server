from pydantic import BaseModel

class MyProfileResponse(BaseModel):
    username: str
    login_id: str

    @staticmethod
    def from_user(user) -> 'MyProfileResponse':
        return MyProfileResponse(
            username=user.username, 
            login_id=user.login_id,
            )

class UserSigninResponse(BaseModel):
    access_token: str
    refresh_token: str

class UserResponse(BaseModel):
    username: str
