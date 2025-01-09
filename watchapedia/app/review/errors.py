from fastapi import HTTPException

class RedundantReviewError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="User already reviewed the movie")

class ReviewNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Review not found")