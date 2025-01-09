from fastapi import HTTPException

class GenreAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Genre already exists")