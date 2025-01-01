from typing import Annotated
from app.movie.repository import MovieRepository
from fastapi import Depends
from common.errors import InvalidCredentialsError, InvalidTokenError, BlockedTokenError
from app.movie.errors import MovieAlreadyExistsError

class MovieService():
    def __init__(self, movie_repository: Annotated[MovieRepository, Depends()]) -> None:
        self.movie_repository = movie_repository
    
    def add_movie(
        self, title: str, year: int, synopsis: str | None, average_rating: float | None, running_time: int, grade: str
    ):
        self.raise_if_movie_exist(title, year, running_time)
        self.movie_repository.add_movie(
            title=title, 
            year=year, 
            synopsis=synopsis or "등록된 소개글이 없습니다.", 
            average_rating=average_rating or 0.0, 
            running_time=running_time, 
            grade=grade
        )

    def raise_if_movie_exist(self, title: str, year: int, running_time: int) -> None:
        if self.movie_repository.get_movie(title, year, running_time) is not None:
            raise MovieAlreadyExistsError()
    
    
    