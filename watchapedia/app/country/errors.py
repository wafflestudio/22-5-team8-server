from fastapi import HTTPException

class CountryAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Country already exists")