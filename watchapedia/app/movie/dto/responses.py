from pydantic import BaseModel
from watchapedia.app.movie.models import Movie

class ParticipantsDataResponse(BaseModel):
    name: str
    role: str
    profile_url: str | None

class MovieDataResponse(BaseModel):
    title: str
    original_title: str
    year: int
    synopsis: str
    average_rating: float | None
    running_time: int
    grade: str | None
    poster_url: str | None
    backdrop_url: str | None
    participants: list[ParticipantsDataResponse]