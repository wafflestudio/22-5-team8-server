from typing import Annotated
from fastapi import Depends
from watchapedia.common.errors import PermissionDeniedError
from watchapedia.app.movie.repository import MovieRepository
from watchapedia.app.movie.errors import MovieNotFoundError
from watchapedia.app.review.dto.responses import ReviewResponse
from watchapedia.app.review.repository import ReviewRepository
from watchapedia.app.review.models import Review
from watchapedia.app.review.errors import RedundantReviewError
from datetime import datetime

class ReviewService:
    def __init__(self,
        movie_repository: Annotated[MovieRepository, Depends()],
        review_repository: Annotated[ReviewRepository, Depends()]
    ) -> None:
        self.movie_repository = movie_repository
        self.review_repository = review_repository

    def create_review(self, user_id: int, movie_id: int, content: str, rating: float | None) -> ReviewResponse:
        movie = self.movie_repository.get_movie_by_movie_id(movie_id)
        if movie is None :
            raise MovieNotFoundError()

        review = self.review_repository.get_review_by_user_and_movie(user_id, movie_id)
        if review is not None :
            raise RedundantReviewError()

        new_review = self.review_repository.create_review(user_id=user_id, movie_id=movie_id,
                                                    content=content, rating=rating, created_at=datetime.now())
        self.movie_repository.update_average_rating(movie)

        return self._process_review_response(new_review)

    def update_review(self, user_id: int, review_id: int, content: str | None, rating: float | None) -> ReviewResponse:
        review = self.review_repository.get_review_by_review_id(review_id)
        if not review.user_id == user_id :
            raise PermissionDeniedError()

        movie = review.movie

        updated_review = self.review_repository.update_review(review, content=content, rating=rating)
        self.movie_repository.update_average_rating(movie)

        return self._process_review_response(updated_review)

    def list_reviews(self, movie_id: int) -> list[ReviewResponse]:
        movie = self.movie_repository.get_movie_by_movie_id(movie_id)
        if movie is None :
            raise MovieNotFoundError()

        reviews = self.review_repository.get_reviews(movie_id)
        return [self._process_review_response(review) for review in reviews]

    def like_review(self, user_id: int, review_id: int) -> ReviewResponse :
        review = self.review_repository.get_review_by_review_id(review_id)
        updated_review = self.review_repository.like_review(user_id, review)
        return self._process_review_response(updated_review)

    def _process_review_response(self, review: Review) -> ReviewResponse:
        return ReviewResponse(
            id=review.id,
            user_id=review.user.id,
            user_name=review.user.username,
            movie_id=review.movie_id,
            content=review.content,
            rating=review.rating,
            likes_count=review.likes_count,
            created_at=review.created_at
        )
