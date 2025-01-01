from fastapi import APIRouter, Depends, Request
from typing import Annotated
from app.movie.service import MovieService
from app.movie.dto.requests import AddMovieRequest

movie_router = APIRouter()

@movie_router.post("", 
                status_code=201,
                summary="영화 추가",
                description="[유저영역 아님] title, year, synopsis, average_rating, running_time, grade를 받아 DB에 영화를 추가하고 성공 시 'Success'를 반환합니다."
)
def add_movie(
    add_movie_request: AddMovieRequest,
    movie_service: Annotated[MovieService, Depends()]
):
    movie_service.add_movie(
        add_movie_request.title, 
        add_movie_request.year, 
        add_movie_request.synopsis, 
        add_movie_request.average_rating, 
        add_movie_request.running_time, 
        add_movie_request.grade
    )
    return "Success"