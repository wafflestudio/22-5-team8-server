from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from database.connection import get_db_session
from typing import Annotated
from datetime import datetime
from app.movie.models import Movie

class MovieRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session
    
    def add_movie(
        self, title: str, year: int, synopsis: str, average_rating: float, running_time: int, grade: str
    ) -> None:
        movie = Movie(
            title=title,
            year=year,
            synopsis=synopsis,
            average_rating=average_rating,
            running_time=running_time,
            grade=grade
        )
        self.session.add(movie)
        self.session.flush()
    
    # 동명의 영화가 다수 존재. 하나로 특정하려면 다른 필드와 조합해서 검색
    def get_movie(self, title: str, year: int, running_time: int) -> Movie | None:
        get_movie_query = select(Movie).filter(
            (Movie.title==title)
            & (Movie.year==year)
            & (Movie.running_time==running_time)
        )
        return self.session.scalar(get_movie_query)

    def get_movie_by_movie_id(self, movie_id: int) -> Movie | None:
        get_movie_query = select(Movie).filter(Movie.id==movie_id)
        return self.session.scalar(get_movie_query)