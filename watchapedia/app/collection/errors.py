from fastapi import HTTPException

class CollectionNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Collection not found")

class InvalidFormatError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Collection Invalid Format")

class NoSuchMovieError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="No Such Movie in the Collection")

class MovieAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Movie already exists in the Collection")

