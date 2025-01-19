from pydantic import BaseModel
from datetime import datetime
from watchapedia.app.user.models import User
from watchapedia.app.comment.models import Comment

class CommentResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    profile_url: str | None
    review_id: int
    content: str
    likes_count: int
    created_at: datetime
    like: bool

