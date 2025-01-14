from fastapi import HTTPException

class CollectionNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Collection not found")