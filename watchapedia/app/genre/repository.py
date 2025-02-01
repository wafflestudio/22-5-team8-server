from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from typing import Annotated
from watchapedia.app.genre.models import Genre
from watchapedia.app.movie.models import Movie
from watchapedia.app.genre.errors import GenreAlreadyExistsError

class GenreRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session
    
    def add_genre(self, name: str) -> Genre:
        if self.get_genre_by_genre_name(name):
            raise GenreAlreadyExistsError()
        genre = Genre(name=name)
        self.session.add(genre)
        self.session.flush()
        return genre
    
    def add_genre_with_movie(self, name: str, movie: Movie) -> None:
        genre = self.get_genre_by_genre_name(name)
        if not genre:
            genre = Genre(name=name)
            self.session.add(genre)
        genre.movies.append(movie)
        self.session.flush()
    
    def get_genre_by_genre_name(self, name: str) -> Genre | None:
        get_genre_query = select(Genre).filter(Genre.name == name)
        return self.session.scalar(get_genre_query)
    
    def get_genres_by_genre_name(self, name: str) -> list[Genre]:
        get_genre_query = select(Genre).filter(
            or_(
                Genre.name.contains(name),
                func.lower(name).like(func.concat("%", Genre.name, "%"))
                #func.lower(name).like(f"%{Genre.name}%")
            )
        )
        return self.session.scalars(get_genre_query).all()
        #get_genre_query = select(Genre).filter(Genre.name.contains(name))
        #return self.session.scalars(get_genre_query).all()

    def get_genre_by_id(self, genre_id: int) -> Genre | None:
        get_genre_query = select(Genre).filter(Genre.id == genre_id)
        return self.session.scalar(get_genre_query)

