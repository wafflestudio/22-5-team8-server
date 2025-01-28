from pydantic import BaseModel

class RecommendResponse(BaseModel):
    movie_id: int
    title: str
    year: int
    countries: list[str]
    expected_rating: float
    poster_url: str | None

