from typing import Annotated
from watchapedia.app.movie.repository import MovieRepository
from watchapedia.app.genre.repository import GenreRepository
from watchapedia.app.country.repository import CountryRepository
from watchapedia.app.participant.repository import ParticipantRepository
from fastapi import Depends
from watchapedia.common.errors import InvalidCredentialsError, InvalidTokenError, BlockedTokenError
from watchapedia.app.movie.errors import MovieAlreadyExistsError
from watchapedia.app.movie.models import Movie
from watchapedia.app.movie.dto.requests import AddParticipantsRequest
from watchapedia.app.movie.dto.responses import MovieDataResponse, ParticipantsDataResponse

class MovieService():
    def __init__(self, 
        movie_repository: Annotated[MovieRepository, Depends()],
        genre_repository: Annotated[GenreRepository, Depends()],
        country_repository: Annotated[CountryRepository, Depends()],
        participant_repository: Annotated[ParticipantRepository, Depends()]) -> None:
        
        self.movie_repository = movie_repository
        self.genre_repository = genre_repository
        self.country_repository = country_repository
        self.participant_repository = participant_repository
    
    def add_movie(
        self, 
        title: str, 
        original_title: str,
        year: int, 
        synopsis: str | None, 
        running_time: int, 
        grade: str | None,
        poster_url: str | None,
        backdrop_url: str | None,
        genres: list[str],
        countries: list[str],
        participants: list[AddParticipantsRequest]
    ) -> MovieDataResponse:
        self.raise_if_movie_exist(title, year, running_time)
        movie = self.movie_repository.add_movie(
            title=title, 
            original_title=original_title,
            year=year, 
            synopsis=synopsis or "등록된 소개글이 없습니다.", 
            running_time=running_time, 
            grade=grade,
            poster_url=poster_url,
            backdrop_url=backdrop_url
        )
        # genre 추가 및 연결
        for genre_name in genres:
            self.genre_repository.add_genre_with_movie(genre_name, movie)
        
        # country 추가 및 연결
        for country_name in countries:
            self.country_repository.add_country_with_movie(country_name, movie)
            
        # participant 추가 및 연결
        participants_list = []
        for participant_data in participants:
            movie_participant = self.participant_repository.add_participant_with_movie(
                participant_data.name, participant_data.profile_url, participant_data.role, movie
            )
            participants_list.append(movie_participant)
        
        return MovieDataResponse(
            id=movie.id,
            title=title,
            original_title=original_title,
            year=year,
            genres=genres,
            countries=countries,
            synopsis=synopsis,
            average_rating=None,
            running_time=running_time,
            grade=grade,
            poster_url=poster_url,
            backdrop_url=backdrop_url,
            participants=[
                ParticipantsDataResponse(
                    name=participant.name,
                    role=participant.role,
                    profile_url=participant.profile_url
                )
                for participant in participants
            ]
        )

    def raise_if_movie_exist(self, title: str, year: int, running_time: int) -> None:
        if self.movie_repository.get_movie(title, year, running_time) is not None:
            # chart update 로직 추가?
            raise MovieAlreadyExistsError()
    
    def get_movie_by_movie_id():
        ...
    
    def get_movie():
        ...
    
    