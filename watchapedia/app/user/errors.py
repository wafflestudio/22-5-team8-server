from fastapi import HTTPException

class UserAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User already exists")

class InvalidTokenError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token")

class UserNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")

class UserAlreadyFollowingError(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User already following")

class UserAlreadyNotFollowingError(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User already not following")

class CANNOT_FOLLOW_MYSELF_Error(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Cannot follow myself")

class CANNOT_BLOCK_MYSELF_Error(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Cannot block myself")