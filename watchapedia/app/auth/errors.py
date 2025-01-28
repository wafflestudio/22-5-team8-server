from fastapi import HTTPException

class AuthorizationCodeNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Authorization code not found")