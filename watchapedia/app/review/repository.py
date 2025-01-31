from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from typing import Annotated, Sequence
from watchapedia.app.user.models import User
from watchapedia.app.review.models import Review, UserLikesReview
from watchapedia.app.review.errors import RedundantReviewError, ReviewNotFoundError
from datetime import datetime

class ReviewRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def get_review_by_user_and_movie(self, user_id: int, movie_id: int) -> Review | None:
        get_review_query = select(Review).filter(
            (Review.user_id == user_id)
            & (Review.movie_id == movie_id)
        )

        return self.session.scalar(get_review_query)

    def create_review(self, user_id: int, movie_id: int, content: str | None, rating: float | None,
                    created_at, spoiler: bool, status: str | None
    ) -> Review:
        review = Review(
            user_id=user_id,
            movie_id=movie_id,
            content=content,
            rating=rating,
            likes_count=0,
            created_at=created_at,
            spoiler=spoiler,
            status=status
        )
        self.session.add(review)
        self.session.flush()

        review = self.get_review_by_user_and_movie(user_id, movie_id)

        return review

    def update_review(self, review, content: str | None, rating: float | None,
                    spoiler: bool | None, status: str | None
    ) -> Review:
        if content is not None :
            review.content = content

        if rating is not None :
            review.rating = rating

        if spoiler is not None :
            review.spoiler = spoiler

        if status is not None :
            review.status = status
        
        self.session.flush()

        return review

    def get_reviews_by_movie_id(self, movie_id: int) -> Sequence[Review]:
        reviews_list_query = select(Review).where(Review.movie_id == movie_id)
        return self.session.scalars(reviews_list_query).all()

    def get_reviews_by_user_id(self, user_id: int) -> Sequence[Review]:
        reviews_list_query = select(Review).where(Review.user_id == user_id)
        return self.session.scalars(reviews_list_query).all()

    def get_review_by_review_id(self, review_id: int) -> Review:
        review = self.session.get(Review, review_id)
        if review is None :
            raise ReviewNotFoundError()

        return review

    def like_info(self, user_id: int, review: Review) -> bool:
        get_like_query = select(UserLikesReview).filter(
            (UserLikesReview.user_id == user_id)
            & (UserLikesReview.review_id == review.id)
        )
        user_likes_review = self.session.scalar(get_like_query)

        if user_likes_review is None :
            return False
        else :
            return True

    def like_review(self, user_id: int, review: Review) -> None:
        get_like_query = select(UserLikesReview).filter(
            (UserLikesReview.user_id == user_id)
            & (UserLikesReview.review_id == review.id)
        )
        user_likes_review = self.session.scalar(get_like_query)

        if user_likes_review is None :
            user_likes_review = UserLikesReview(
                user_id=user_id,
                review_id=review.id,
            )
            self.session.add(user_likes_review)

            review.likes_count += 1

        else :
            self.session.delete(user_likes_review)

            review.likes_count -= 1
        
        self.session.flush()

        return review

    def delete_review_by_id(self, review: Review) -> None:
        self.session.delete(review)
        self.session.flush()
