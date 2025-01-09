from typing import Annotated
from watchapedia.app.movie.repository import MovieRepository
from watchapedia.app.genre.repository import GenreRepository
from watchapedia.app.country.repository import CountryRepository
from watchapedia.app.participant.repository import ParticipantRepository
from fastapi import Depends
from watchapedia.app.movie.errors import MovieAlreadyExistsError, MovieNotFoundError, InvalidFormatError
from watchapedia.app.movie.models import Movie
from watchapedia.app.movie.dto.requests import AddParticipantsRequest, AddMovieListRequest
from watchapedia.app.movie.dto.responses import MovieDataResponse, ParticipantsDataResponse

class MovieService():
    def __init__(self, 
        movie_repository: Annotated[MovieRepository, Depends()],
        genre_repository: Annotated[GenreRepository, Depends()],
        country_repository: Annotated[CountryRepository, Depends()],
        participant_repository: Annotated[ParticipantRepository, Depends()]
    ) -> None:     
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
        participants: list[AddParticipantsRequest],
        chart_type: str | None = None,
        rank: int | None = None
    ) -> MovieDataResponse:
        
        movie = self.raise_if_movie_exist(title, year, running_time, chart_type, rank)
        if movie is None:
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

            # chart crawling의 경우, 차트 추가 및 연결
            if chart_type and rank:
                self.movie_repository.update_chart(chart_type, rank, movie)
        
        return self._process_movie_response(movie)

    def raise_if_movie_exist(
        self, title: str, year: int, running_time: int, chart_type: str | None, rank: int | None
    ) -> Movie | None:
        """
        이미 해당 영화가 존재하고, 차트 정보가 업데이트 되었을 때 Movie 객체 반환.
        
        존재하지 않는 영화인 경우 None 반환
        """
        movie = self.movie_repository.get_movie(title, year, running_time)
        if movie:
            if not chart_type and not rank:
                raise MovieAlreadyExistsError()
            else:
                self.movie_repository.update_chart(chart_type, rank, movie)
        return movie
    
    def search_movie(self, movie_id: int):
        movie = self.movie_repository.get_movie_by_movie_id(movie_id)
        if movie is None:
            raise MovieNotFoundError()
        return self._process_movie_response(movie)
    
    def update_movie(
        self, 
        movie_id: int, 
        synopsis: str | None, 
        grade: str | None, 
        average_rating: float | None, 
        poster_url: str | None, 
        backdrop_url: str | None
    ) -> None:
        movie = self.movie_repository.get_movie_by_movie_id(movie_id)
        if not movie:
            raise MovieNotFoundError()
        if not any([synopsis, grade, average_rating, poster_url, backdrop_url]):
            raise InvalidFormatError()
        self.movie_repository.update_movie(
            movie=movie,
            synopsis=synopsis,
            grade=grade,
            average_rating=average_rating,
            poster_url=poster_url,
            backdrop_url=backdrop_url
        )
    
    def search_movie_list(
        self,
        title: str | None = None,
        chart_type: str | None = None,
        min_rating: float | None = None,
        max_rating: float | None = None,
        genres: list[str] | None = None,
        countries: list[str] | None = None,
        participant_id: int | None = None
    ) -> list[MovieDataResponse]:
        if not any([title, chart_type, min_rating, max_rating, genres, countries, participant_id]):
            raise InvalidFormatError()
        movies = self.movie_repository.search_movie_list(
            title=title,
            chart_type=chart_type,
            min_rating=min_rating,
            max_rating=max_rating,
            genres=genres,
            countries=countries,
            participant_id=participant_id
        )
        return [ self._process_movie_response(movie) for movie in movies ]
        
    def add_movie_list(self, movie_list_request: list[AddMovieListRequest]) -> list[MovieDataResponse]:
        movie_response_list = []
        for movie_request in movie_list_request:
            movie_response = self.add_movie(
                movie_request.title,
                movie_request.original_title,
                movie_request.year,
                movie_request.synopsis,
                movie_request.running_time,
                movie_request.grade,
                movie_request.poster_url,
                movie_request.backdrop_url,
                movie_request.genres,
                movie_request.countries,
                movie_request.participants,
                movie_request.chart_type,
                movie_request.rank,
            )
            movie_response_list.append(movie_response)
        return movie_response_list
    
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
            ratings_count=len(movie.reviews),
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
    
    