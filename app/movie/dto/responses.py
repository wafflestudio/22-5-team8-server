from pydantic import BaseModel
from app.movie.models import Movie

class MovieDataResponse(BaseModel):
    title: str
    year: int
    synopsis: str
    average_rating: float
    running_time: int
    grade: str

    @staticmethod
    def from_movie(movie: Movie) -> "MovieDataResponse":
        return MovieDataResponse(
            title=movie.title,
            year=movie.year,
            synopsis=movie.synopsis,
            average_rating=movie.average_rating,
            running_time=movie.running_time,
            grade=movie.grade
        )