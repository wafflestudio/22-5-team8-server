from pydantic import BaseModel
from watchapedia.app.movie.models import Movie

class MovieDataResponse(BaseModel):
    title: str
    year: int
    synopsis: str
    average_rating: float
    running_time: int
    grade: str
    poster_url: str
    backdrop_url: str

    @staticmethod
    def from_movie(movie: Movie) -> "MovieDataResponse":
        return MovieDataResponse(
            title=movie.title,
            year=movie.year,
            synopsis=movie.synopsis,
            average_rating=movie.average_rating,
            running_time=movie.running_time,
            grade=movie.grade,
            poster_url=movie.poster_url,
            backdrop_url=movie.backdrop_url
        )