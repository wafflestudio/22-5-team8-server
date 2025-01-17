from typing import Annotated
from fastapi import Depends
from watchapedia.common.errors import PermissionDeniedError
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

        return self._process_comment_response(new_comment)

    def update_comment(self, user_id: int, comment_id: int, content: str) -> CommentResponse:
        comment = self.comment_repository.get_comment_by_comment_id(comment_id)
        if not comment.user_id == user_id :
            raise PermissionDeniedError()

        updated_comment = self.comment_repository.update_comment(comment, content=content)
        return self._process_comment_response(updated_comment)

    def list_comments(self, review_id: int) -> list[CommentResponse]:
        review = self.review_repository.get_review_by_review_id(review_id)
        if review is None :
            raise ReviewNotFoundError()

        comments = self.comment_repository.get_comments(review_id)
        return [self._process_comment_response(comment) for comment in comments]

    def like_comment(self, user_id: int, comment_id: int) -> CommentResponse :
        comment = self.comment_repository.get_comment_by_comment_id(comment_id)
        if comment is None :
            raise CommentNotFoundError()

        updated_comment = self.comment_repository.like_comment(user_id, comment)
        return self._process_comment_response(updated_comment)

    def _process_comment_response(self, comment: Comment) -> CommentResponse:
        return CommentResponse(
            id=comment.id,
            user_id=comment.user.id,
            user_name=comment.user.username,
            profile_url=comment.user.profile_url,
            review_id=comment.review_id,
            content=comment.content,
            likes_count=comment.likes_count,
            created_at=comment.created_at
        )
