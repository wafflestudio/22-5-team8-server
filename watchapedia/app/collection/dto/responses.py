from pydantic import BaseModel
from datetime import datetime

class MovieCompactResponse(BaseModel):
    id: int
    title: str
    poster_url: str | None
    average_rating: float | None

class CollectionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    overview: str | None
    likes_count: int
    comments_count: int
    created_at: datetime
    movies: list[MovieCompactResponse]