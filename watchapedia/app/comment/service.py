from typing import Annotated
from fastapi import Depends
from watchapedia.common.errors import PermissionDeniedError, InvalidRangeError
from watchapedia.app.review.repository import ReviewRepository
from watchapedia.app.review.errors import ReviewNotFoundError
from watchapedia.app.comment.dto.responses import CommentResponse
from watchapedia.app.comment.repository import CommentRepository
from watchapedia.app.comment.models import Comment
from watchapedia.app.comment.errors import RedundantCommentError, CommentNotFoundError
from datetime import datetime

class CommentService:
    def __init__(self,
    review_repository: Annotated[ReviewRepository, Depends()],
    comment_repository: Annotated[CommentRepository, Depends()]
    ) -> None:
        self.review_repository = review_repository
        self.comment_repository = comment_repository

    def create_comment(self, user_id: int, review_id: int, content: str) -> CommentResponse:
        review = self.review_repository.get_review_by_review_id(review_id)
        if review is None :
            raise ReviewNotFoundError()

        new_comment = self.comment_repository.create_comment(user_id=user_id, review_id=review_id,
                                                    content=content, created_at=datetime.now())

        return self._process_comment_response(user_id, new_comment)

    def update_comment(self, user_id: int, comment_id: int, content: str) -> CommentResponse:
        comment = self.comment_repository.get_comment_by_comment_id(comment_id)
        if not comment.user_id == user_id :
            raise PermissionDeniedError()

        updated_comment = self.comment_repository.update_comment(comment, content=content)
        return self._process_comment_response(user_id, updated_comment)


    def get_comment(self, comment_id: int) -> CommentResponse:
        comment = self.comment_repository.get_comment_by_comment_id(comment_id)
        return self._process_comment_response(-1, comment)

    def review_comments(self, review_id: int, begin: int | None, end: int | None) -> list[CommentResponse]:
        review = self.review_repository.get_review_by_review_id(review_id)
        if review is None :
            raise ReviewNotFoundError()

        comments = self.comment_repository.get_comments_by_review_id(review_id)
        return self._process_range([self._process_comment_response(-1, comment) for comment in comments], begin, end)

    def review_user_comments(self, user_id: int, review_id: int, begin: int | None, end: int | None) -> list[CommentResponse]:
        review = self.review_repository.get_review_by_review_id(review_id)
        if review is None :
            raise ReviewNotFoundError()

        comments = self.comment_repository.get_comments_by_review_id(review_id)
        return self._process_range([self._process_comment_response(user_id, comment) for comment in comments], begin, end)

    def user_comments(self, user_id: int, begin: int | None, end: int | None) -> list[CommentResponse]:
        comments = self.comment_repository.get_comments_by_user_id(user_id)
        return self._process_range([self._process_comment_response(user_id, comment) for comment in comments], begin, end)


    def like_comment(self, user_id: int, comment_id: int) -> CommentResponse :
        comment = self.comment_repository.get_comment_by_comment_id(comment_id)
        if comment is None :
            raise CommentNotFoundError()

        updated_comment = self.comment_repository.like_comment(user_id, comment)
        return self._process_comment_response(user_id, updated_comment)

    def delete_comment_by_id(self, user_id: int, comment_id: int) -> None:
        comment = self.comment_repository.get_comment_by_comment_id(comment_id)
        if comment is None:
            raise CommentNotFoundError()
        if comment.user_id != user_id:
            raise PermissionDeniedError()
        self.comment_repository.delete_comment_by_id(comment)

    
    def _process_range(self, response_list, begin: int | None, end: int | None) -> list[CommentResponse]:
        if begin is None :
            begin = 0
        if end is None or end > len(response_list) :
            end = len(response_list)
        if begin > len(response_list) :
            begin = len(response_list)
        if begin < 0 or begin > end :
            raise InvalidRangeError()
        return response_list[begin : end]

    def _process_comment_response(self, user_id: int, comment: Comment) -> CommentResponse:
        return CommentResponse(
            id=comment.id,
            user_id=comment.user.id,
            user_name=comment.user.username,
            profile_url=comment.user.profile_url,
            review_id=comment.review_id,
            content=comment.content,
            likes_count=comment.likes_count,
            created_at=comment.created_at,
            like=self.comment_repository.like_info(user_id, comment)
        )
