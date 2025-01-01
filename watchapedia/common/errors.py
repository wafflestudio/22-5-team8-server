from fastapi import HTTPException

class InvalidFieldFormatError(HTTPException):
    def __init__(self, field_name: str):
        super().__init__(status_code=400, detail=f"Invalid format for field {field_name}")

class MissingRequiredFieldError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Missing required field")

class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid credentials")

class ExpiredSignatureError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Expired signature")

class InvalidTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Invalid token")

class BlockedTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Blocked token")