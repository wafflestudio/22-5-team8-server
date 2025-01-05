from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from typing import Annotated
from watchapedia.app.country.models import Country
from watchapedia.app.movie.models import Movie
from watchapedia.app.country.errors import CountryAlreadyExistsError

class CountryRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session
    
    def add_country(self, name: str) -> Country:
        if self.get_country_by_country_name(name):
            raise CountryAlreadyExistsError()
        country = Country(name=name)
        self.session.add(country)
        self.session.flush()
        return country
    
    def add_country_with_movie(self, name: str, movie: Movie) -> None:
        if self.get_country_by_country_name(name):
            raise CountryAlreadyExistsError()
        country = Country(name=name)
        country.movies.append(movie)
        self.session.add(country)
        self.session.flush()
    
    def get_country_by_country_name(self, name: str) -> Country | None:
        get_country_query = select(Country).filter(Country.name == name)
        return self.session.scalar(get_country_query)