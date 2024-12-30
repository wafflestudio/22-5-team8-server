from pydantic import BaseModel

class MyProfileResponse(BaseModel):
    username: str
    login_id: str
    hashed_pwd: str

    @staticmethod
    def from_user(user) -> 'MyProfileResponse':
        return MyProfileResponse(
            username=user.username, 
            login_id=user.login_id, 
            hashed_pwd=user.hashed_pwd
            )

class UserSigninResponse(BaseModel):
    access_token: str
    refresh_token: str