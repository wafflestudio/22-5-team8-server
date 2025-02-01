from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from typing import Annotated
from datetime import datetime
from watchapedia.app.user.views import login_with_header
from watchapedia.app.user.models import User
from watchapedia.app.review.dto.requests import ReviewCreateRequest, ReviewUpdateRequest, validate_date_query
from watchapedia.app.review.dto.responses import ReviewResponse
from watchapedia.app.review.models import Review
from watchapedia.app.review.service import ReviewService
from watchapedia.app.review.errors import *

review_router = APIRouter()

@review_router.post('/{movie_id}',
                status_code=201, 
                summary="리뷰 작성", 
                description="movie_id, content와 rating, spoiler 여부를 받아 리뷰를 작성하고 성공 시 username을 포함하여 리뷰를 반환합니다.",
            )
def create_review(
    user: Annotated[User, Depends(login_with_header)],
    movie_id: int,
    review_service: Annotated[ReviewService, Depends()],
    review: ReviewCreateRequest,
) -> ReviewResponse:
    return review_service.create_review(user.id, movie_id, review.content,
                                        review.rating, review.spoiler, review.status)

@review_router.patch('/{review_id}',
                status_code=200, 
                summary="리뷰 수정", 
                description="review_id와 content, rating, spoiler 여부를 받아 리뷰를 수정하고 반환합니다.",
                response_model=ReviewResponse
                )
def update_review(
    user: Annotated[User, Depends(login_with_header)],
    review_id: int,
    review: ReviewUpdateRequest,
    review_service: Annotated[ReviewService, Depends()],
):
    return review_service.update_review(
        user.id, review_id, review.content, review.rating, review.spoiler, review.status
    )


@review_router.post('/date/{review_id}',
                status_code=200,
                summary="본 날짜추가",
                description="review_id와 새로운 날짜를 받아 view_date에 추가합니다.",
                response_model=ReviewResponse
                )
def add_view_date(
        user: Annotated[User, Depends(login_with_header)],
        review_id: int,
        review_service: Annotated[ReviewService, Depends()],
        new_view_date: Annotated[str, Query(..., description="추가할 날짜 (YYYY-MM-DD)")]
        ):
    new_view_date = validate_date_query(new_view_date)
    return review_service.add_view_date(
            user.id, review_id, new_view_date)


@review_router.delete('/date/{review_id}',
                status_code=204,
                summary="본 날짜삭제",
                description="review_id와 삭제할 날짜를 받아 view_date에 삭제합니다."
                )
def delete_view_date(
        user: Annotated[User, Depends(login_with_header)],
        review_id: int,
        review_service: Annotated[ReviewService, Depends()],
        delete_view_date: Annotated[str, Query(..., description="삭제할 날짜 (YYYY-MM-DD)")]
        ):
    delete_view_date = validate_date_query(delete_view_date)
    review_service.delete_view_date(user.id, review_id, delete_view_date)


@review_router.get('/user',
                status_code=200, 
                summary="자기 리뷰 출력", 
                description="[로그인 필요] 자신이 남긴 모든 리뷰들을 반환합니다",
                response_model=list[ReviewResponse]
            )
def get_reviews(
    user: Annotated[User, Depends(login_with_header)],
    review_service: Annotated[ReviewService, Depends()],
    begin: int | None = None,
    end: int | None = None,
):
    return review_service.user_reviews(user.id, begin, end)

@review_router.get('/user/{user_id}',
                status_code=200,
                summary="유저 리뷰 출력", 
                description="[로그인 불필요] user_id를 받아 해당 유저가 남긴 모든 리뷰들을 반환합니다",
                response_model=list[ReviewResponse]
            )
def get_reviews_by_user(
    user_id: int,
    review_service: Annotated[ReviewService, Depends()],
    begin: int | None = None,
    end: int | None = None,
):
    return review_service.user_reviews(user_id, begin, end)

@review_router.get('/movie/{movie_id}',
                status_code=200, 
                summary="비로그인 리뷰 출력", 
                description="[로그인 불필요] movie_id를 받아 해당 영화에 달린 리뷰들을 반환합니다",
                response_model=list[ReviewResponse]
                )
def get_reviews_by_movie(
    movie_id: int,
    review_service: Annotated[ReviewService, Depends()],
    begin: int | None = None,
    end: int | None = None,
):
    return review_service.movie_reviews(movie_id, begin, end)
    
@review_router.get('/list/{movie_id}',
                status_code=200, 
                summary="로그인 리뷰 출력", 
                description="[로그인 필요] 유저가 남긴 모든 리뷰들을 반환합니다",
                response_model=list[ReviewResponse]
            )
def get_reviews_by_movie_and_user(
    user: Annotated[User, Depends(login_with_header)],
    movie_id: int,
    review_service: Annotated[ReviewService, Depends()],
    begin: int | None = None,
    end: int | None = None,
):
    return review_service.movie_user_reviews(user.id, movie_id, begin, end)

@review_router.get('/{review_id}',
                status_code=200, 
                summary="단일 리뷰 출력", 
                description="[로그인 불필요] review_id를 받아 해당 리뷰를 반환합니다",
                response_model=ReviewResponse
            )
def get_review(
    review_id: int,
    review_service: Annotated[ReviewService, Depends()],
):
    return review_service.get_review(review_id)

@review_router.patch('/like/{review_id}',
                status_code=200, 
                summary="리뷰 추천/취소", 
                description="review_id를 받아 추천되어 있지 않으면 추천하고, 추천되어 있으면 취소합니다.",
                response_model=ReviewResponse
            )
def like_review(
    user: Annotated[User, Depends(login_with_header)],
    review_id: int,
    review_service: Annotated[ReviewService, Depends()],
):
    return review_service.like_review(user.id, review_id)

@review_router.delete('/{review_id}',
                status_code=204,
                summary="리뷰 삭제",
                description="[로그인 필요] 리뷰 id를 받아 해당 리뷰를 삭제합니다. 성공 시 204 code 반환")
def delete_review(
    review_id: int,
    user: Annotated[User, Depends(login_with_header)],
    review_service: Annotated[ReviewService, Depends()]
):
    review_service.delete_review_by_id(user.id, review_id)
