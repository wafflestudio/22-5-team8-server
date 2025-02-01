from typing import Annotated
from fastapi import Depends
from watchapedia.common.errors import PermissionDeniedError, InvalidRangeError
from watchapedia.app.user.models import User
from watchapedia.app.movie.repository import MovieRepository
from watchapedia.app.movie.errors import MovieNotFoundError
from watchapedia.app.review.dto.responses import ReviewResponse
from watchapedia.app.review.repository import ReviewRepository
from watchapedia.app.comment.repository import CommentRepository
from watchapedia.app.review.models import Review
from watchapedia.app.review.errors import RedundantReviewError, ReviewNotFoundError
from datetime import datetime, date
from watchapedia.app.analysis.service import UserRatingService, UserPreferenceService

class ReviewService:
    def __init__(self,
        movie_repository: Annotated[MovieRepository, Depends()],
        review_repository: Annotated[ReviewRepository, Depends()],
        comment_repository: Annotated[CommentRepository, Depends()],
        user_rating_service: Annotated[UserRatingService, Depends()],
        user_preference_service: Annotated[UserPreferenceService, Depends()]
    ) -> None:
        self.movie_repository = movie_repository
        self.review_repository = review_repository
        self.comment_repository = comment_repository

        self.user_rating_service = user_rating_service
        self.user_preference_service = user_preference_service

    def create_review(self, user_id: int, movie_id: int, content: str | None,
                    rating: float | None, spoiler: bool, status: str | None
    ) -> ReviewResponse:
        movie = self.movie_repository.get_movie_by_movie_id(movie_id)
        if movie is None :
            raise MovieNotFoundError()

        review = self.review_repository.get_review_by_user_and_movie(user_id, movie_id)
        if review is not None :
            raise RedundantReviewError()

        new_review = self.review_repository.create_review(user_id=user_id, movie_id=movie_id, content=content, rating=rating,
                                                        created_at=datetime.now(), spoiler=spoiler, status=status)
        self.movie_repository.update_average_rating(movie)

        self.user_rating_service.update_rating(user_id)
        self.user_preference_service.update_preference(user_id, new_review.id)

        return self._process_review_response(user_id, new_review)

    def update_review(self, user_id: int, review_id: int, content: str | None,
                    rating: float | None, spoiler: bool | None, status: str | None
    ) -> ReviewResponse:
        review = self.review_repository.get_review_by_review_id(review_id)
        if not review.user_id == user_id :
            raise PermissionDeniedError()

        movie = review.movie

        updated_review = self.review_repository.update_review(review, content=content, rating=rating,
                                                            spoiler=spoiler, status=status)
        self.movie_repository.update_average_rating(movie)

        self.user_rating_service.update_rating(user_id)
        self.user_preference_service.update_preference(user_id, review_id)

        return self._process_review_response(user_id, updated_review)
    
    def add_view_date(self, user_id: int, review_id: int, new_view_date: date) -> ReviewResponse:
        review = self.review_repository.get_review_by_review_id(review_id)
        view_date = review.view_date

        # date -> str 변환
        new_view_date = new_view_date.strftime("%Y-%m-%d") 
        if new_view_date not in view_date.keys():
            updated_review = self.review_repository.add_view_date(review, new_view_date)
        else:
            raise InvalidRangeError() # 존재하는 시청날짜 
        return self._process_review_response(user_id, updated_review)

    def delete_view_date(self, user_id: int, review_id: int, delete_view_date: date) -> ReviewResponse:
        review = self.review_repository.get_review_by_review_id(review_id)
        view_date = review.view_date
        # date -> str 변환
        delete_view_date = delete_view_date.strftime("%Y-%m-%d")
        if delete_view_date in view_date.keys():
            if len(view_date) == 1:
                raise InvalidRangeError() # 시청기록1회는삭제불가 
            else:
                updated_review = self.review_repository.delete_view_date(review, delete_view_date)
        else:
            raise InvalidRangeError() # 해당날짜 시청기록없음 
        return self._process_review_response(user_id, updated_review)

    def get_review_by_user_and_movie(self, user_id: int, movie_id: int) -> ReviewResponse:
        review = self.review_repository.get_review_by_user_and_movie(user_id, movie_id)
        if review is None :
            return None
        return self._process_review_response(-1, review)

    def get_review(self, review_id: int) -> ReviewResponse:
        review = self.review_repository.get_review_by_review_id(review_id)
        return self._process_review_response(-1, review)

    def movie_reviews(self, movie_id: int, begin: int | None, end: int | None) -> list[ReviewResponse]:
        movie = self.movie_repository.get_movie_by_movie_id(movie_id)
        if movie is None :
            raise MovieNotFoundError()

        reviews = self.review_repository.get_reviews_by_movie_id(movie_id)
        return self._process_range([self._process_review_response(-1, review) for review in reviews], begin, end)

    def movie_user_reviews(self, user_id: int, movie_id: int, begin: int | None, end: int | None) -> list[ReviewResponse]:
        movie = self.movie_repository.get_movie_by_movie_id(movie_id)
        if movie is None :
            raise MovieNotFoundError()

        reviews = self.review_repository.get_reviews_by_movie_id(movie_id)
        return self._process_range([self._process_review_response(user_id, review) for review in reviews], begin, end)

    def user_reviews(self, user_id: int, begin: int | None, end: int | None) -> list[ReviewResponse]:
        reviews = self.review_repository.get_reviews_by_user_id(user_id)
        return self._process_range([self._process_review_response(user_id, review) for review in reviews], begin, end)


    def like_review(self, user_id: int, review_id: int) -> ReviewResponse :
        review = self.review_repository.get_review_by_review_id(review_id)
        updated_review = self.review_repository.like_review(user_id, review)
        return self._process_review_response(user_id, updated_review)
    
    def get_like_review_list(self, user_id: int) -> list[ReviewResponse]:
        reviews = self.review_repository.get_like_review_list(user_id)
        return [self._process_review_response(user_id, review) for review in reviews]

    def delete_review_by_id(self, user_id: int, review_id: int) -> None:
        review = self.review_repository.get_review_by_review_id(review_id)
        if review is None:
            raise ReviewNotFoundError()
        if review.user_id != user_id:
            raise PermissionDeniedError()

        movie_id = review.movie_id # 삭제전 movie_id 저장
        self.review_repository.delete_review_by_id(review)

        self.user_rating_service.update_rating(user_id)
        self.user_preference_service.update_preference(user_id, review_id, delete=True, movie_id=movie_id)


    def _process_range(self, response_list, begin: int | None, end: int | None) -> list[ReviewResponse]:
        if begin is None :
            begin = 0
        if end is None or end > len(response_list) :
            end = len(response_list)
        if begin > len(response_list) :
            begin = len(response_list)
        if begin < 0 or begin > end :
            raise InvalidRangeError()
        return response_list[begin : end]

    def _process_review_response(self, user_id: int, review: Review) -> ReviewResponse:
        return ReviewResponse(
            id=review.id,
            user_id=review.user.id,
            user_name=review.user.username,
            profile_url=review.user.profile_url,
            movie_id=review.movie_id,
            content=review.content,
            rating=review.rating,
            likes_count=review.likes_count,
            created_at=review.created_at,
            view_date=review.view_date,
            spoiler=review.spoiler,
            status=review.status,
            like=self.review_repository.like_info(user_id, review),
            comments_count=self.comment_repository.get_comments_count_by_review_id(review.id)
        )
