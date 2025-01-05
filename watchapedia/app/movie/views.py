from fastapi import APIRouter, Depends, Request
from typing import Annotated
from watchapedia.app.movie.service import MovieService
from watchapedia.app.movie.dto.requests import AddMovieRequest
from watchapedia.app.movie.dto.responses import MovieDataResponse

movie_router = APIRouter()

@movie_router.post("", 
                status_code=201,
                summary="영화 추가",
                description="[유저영역 아님] 영화 정보를 받아 DB에 영화를 추가하고 성공 시 저장된 정보를 반환합니다."
)
def add_movie(
    add_movie_request: AddMovieRequest,
    movie_service: Annotated[MovieService, Depends()]
) -> MovieDataResponse:
    return movie_service.add_movie(
        add_movie_request.title, 
        add_movie_request.original_title,
        add_movie_request.year, 
        add_movie_request.synopsis,
        add_movie_request.running_time, 
        add_movie_request.grade,
        add_movie_request.poster_url,
        add_movie_request.backdrop_url,
        add_movie_request.genres,
        add_movie_request.countries,
        add_movie_request.participants
    )