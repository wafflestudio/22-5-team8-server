from pydantic import BaseModel

class MovieDataResponse(BaseModel):
    id: int
    title: str
    year: int
    average_rating: float | None
    poster_url: str | None


class ParticipantDataResponse(BaseModel):
    cast: str
    movies: list[MovieDataResponse]