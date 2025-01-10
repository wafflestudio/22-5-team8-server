from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
from datetime import datetime
from watchapedia.app.user.views import login_with_header
from watchapedia.app.user.models import User
from watchapedia.app.review.dto.requests import ReviewCreateRequest, ReviewUpdateRequest
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

@review_router.get('/list',
                status_code=200, 
                summary="유저 리뷰 출력", 
                description="유저가 남긴 모든 리뷰들을 반환합니다다",
                response_model=list[ReviewResponse]
            )
def get_reviews_by_user(
    user: Annotated[User, Depends(login_with_header)],
    review_service: Annotated[ReviewService, Depends()],
):
    return review_service.user_reviews(user)

@review_router.get('/list/{movie_id}',
                status_code=200, 
                summary="영화 리뷰 출력", 
                description="movie_id를 받아 해당 영화에 달린 리뷰들을 반환합니다",
                response_model=list[ReviewResponse]
                )
def get_reviews_by_movie(
    movie_id: int,
    review_service: Annotated[ReviewService, Depends()],
):
    return review_service.movie_reviews(movie_id)

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