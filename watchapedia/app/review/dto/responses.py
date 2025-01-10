from pydantic import BaseModel
from datetime import datetime
from watchapedia.app.user.models import User
from watchapedia.app.review.models import Review

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    movie_id: int
    content: str | None
    rating: float | None
    likes_count: int
    created_at: datetime
    spoiler: bool
    status: str | None

