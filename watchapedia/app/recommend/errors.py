from fastapi import HTTPException

class NotEnoughRatingError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="User doesn't have enough ratings")