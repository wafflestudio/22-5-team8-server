from pydantic import BaseModel

class UserSigninResponse(BaseModel):
    access_token: str
    refresh_token: str