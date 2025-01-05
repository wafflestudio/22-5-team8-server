from fastapi import HTTPException

class MovieAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Movie already exists")

class MovieNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Movie Not Found")

class InvalidUpdateError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid Update")