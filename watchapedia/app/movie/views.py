from fastapi import APIRouter, Depends, Request
from typing import Annotated
from watchapedia.app.movie.service import MovieService
from watchapedia.app.movie.dto.requests import AddMovieRequest, UpdateMovieRequest
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

@movie_router.get("/{movie_id}",
                status_code=200,
                summary="영화 조회",
                description="영화 id로 DB를 조회하여 성공 시 영화 정보를 반환합니다.")
def get_movie(
    movie_id: int,
    movie_service: Annotated[MovieService, Depends()]
) -> MovieDataResponse:
    return movie_service.search_movie(movie_id)

@movie_router.patch("/{movie_id}",
                status_code=200,
                summary="영화 정보 업데이트",
                description="특정 영화의 데이터를 업데이트 한 후 성공 시 'Success'를 반환합니다. 업데이트 가능한 항목은 synopsis, grade, poster_url, backdrop_url 입니다.")
def update_movie(
    movie_id: int,
    update_movie_request: UpdateMovieRequest,
    movie_service: Annotated[MovieService, Depends()]
):
    movie_service.update_movie(
        movie_id,
        update_movie_request.synopsis,
        update_movie_request.grade,
        update_movie_request.poster_url,
        update_movie_request.backdrop_url
    )
    return 'Success'