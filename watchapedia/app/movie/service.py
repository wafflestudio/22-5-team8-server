from typing import Annotated
from watchapedia.app.movie.repository import MovieRepository
from watchapedia.app.genre.repository import GenreRepository
from watchapedia.app.country.repository import CountryRepository
from watchapedia.app.participant.repository import ParticipantRepository
from fastapi import Depends
from watchapedia.app.movie.errors import MovieAlreadyExistsError, MovieNotFoundError, InvalidUpdateError
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
        for participant_data in participants:
            self.participant_repository.add_participant_with_movie(
                participant_data.name, participant_data.profile_url, participant_data.role, movie
            )
        
        return self._process_movie_response(movie)

    def raise_if_movie_exist(self, title: str, year: int, running_time: int) -> None:
        if self.movie_repository.get_movie(title, year, running_time) is not None:
            # chart update 로직 추가?
            raise MovieAlreadyExistsError()
    
    def search_movie(self, movie_id: int):
        movie = self.movie_repository.get_movie_by_movie_id(movie_id)
        if movie is None:
            raise MovieNotFoundError()
        return self._process_movie_response(movie)
    
    def update_movie(
        self, movie_id: int, synopsis: str | None, grade: str | None, poster_url: str | None, backdrop_url: str | None
    ) -> None:
        movie = self.movie_repository.get_movie_by_movie_id(movie_id)
        if not movie:
            raise MovieNotFoundError()
        if not any([synopsis, grade, poster_url, backdrop_url]):
            raise InvalidUpdateError()
        self.movie_repository.update_movie(
            movie=movie,
            synopsis=synopsis,
            grade=grade,
            poster_url=poster_url,
            backdrop_url=backdrop_url
        )
        
    
    def get_movie():
        ...
        
    def _process_movie_response(self, movie: Movie) -> MovieDataResponse:
        return MovieDataResponse(
            id=movie.id,
            title=movie.title,
            original_title=movie.original_title,
            year=movie.year,
            genres=[
                genre.name for genre in movie.genres    
            ],
            countries=[
                country.name for country in movie.countries
            ],
            synopsis=movie.synopsis,
            average_rating=movie.average_rating,
            running_time=movie.running_time,
            grade=movie.grade,
            poster_url=movie.poster_url,
            backdrop_url=movie.backdrop_url,
            participants=[
                ParticipantsDataResponse(
                    id=participant.participant_id,
                    name=participant.participant.name,
                    role=participant.role,
                    profile_url=participant.participant.profile_url
                )
                for participant in movie.movie_participants
            ]
        )
    
    