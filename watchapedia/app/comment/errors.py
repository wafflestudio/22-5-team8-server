from fastapi import HTTPException

class RedundantCommentError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="User already made a comment")

class CommentNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Comment not found")