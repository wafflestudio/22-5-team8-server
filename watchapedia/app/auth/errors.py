from fastapi import HTTPException

class GoogleRegisterError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Google Register Error")

class InvalidLoginProviderError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid Login Provider")

class GoogleOAuthError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Google OAuth Error")