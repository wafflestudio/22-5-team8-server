from pydantic import BaseModel
from datetime import datetime
from watchapedia.app.user.models import User
from watchapedia.app.review.models import Review

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    profile_url: str | None
    movie_id: int
    content: str | None
    rating: float | None
    likes_count: int
    created_at: datetime
    view_date: dict[str, bool] | None
    spoiler: bool
    status: str | None
    like: bool
    comments_count: int
