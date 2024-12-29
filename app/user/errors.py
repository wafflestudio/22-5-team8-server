from fastapi import HTTPException

class UserAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User already exists")

class InvalidTokenError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token")