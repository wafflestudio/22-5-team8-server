from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from typing import Annotated, Sequence
from datetime import datetime
from watchapedia.app.comment.models import Comment, UserLikesComment
from watchapedia.app.comment.errors import CommentNotFoundError

class CommentRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def get_comment_by_user_and_review(self, user_id: int, review_id: int) -> Comment | None:
        get_comment_query = select(Comment).filter(
            (Comment.user_id == user_id)
            & (Comment.review_id == review_id)
        )

        return self.session.scalar(get_comment_query)

    def create_comment(self, user_id: int, review_id: int, content: str, created_at) -> Comment:
        comment = Comment(
            user_id=user_id,
            review_id=review_id,
            content=content,
            likes_count=0,
            created_at=created_at
        )
        self.session.add(comment)
        self.session.flush()

        comment = self.get_comment_by_user_and_review(user_id, review_id)

        return comment

    def update_comment(self, comment, content: str) -> Comment:
        comment.content = content
        self.session.flush()

        return comment

    def get_comments_by_review_id(self, review_id: int) -> Sequence[Comment]:
        comments_list_query = select(Comment).where(Comment.review_id == review_id)
        return self.session.scalars(comments_list_query).all()

    def get_comments_by_user_id(self, user_id: int) -> Sequence[Comment]:
        comments_list_query = select(Comment).where(Comment.user_id == user_id)
        return self.session.scalars(comments_list_query).all()

    def get_comment_by_comment_id(self, comment_id: int) -> Comment:
        comment = self.session.get(Comment, comment_id)
        if comment is None :
            raise CommentNotFoundError()

        return comment

    def like_info(self, user_id: int, comment: Comment) -> bool :
        get_like_query = select(UserLikesComment).filter(
            (UserLikesComment.user_id == user_id)
            & (UserLikesComment.comment_id == comment.id)
        )
        user_likes_comment = self.session.scalar(get_like_query)

        if user_likes_comment is None :
            return False
        else :
            return True

    def like_comment(self, user_id: int, comment: Comment) -> Comment:
        get_like_query = select(UserLikesComment).filter(
            (UserLikesComment.user_id == user_id)
            & (UserLikesComment.comment_id == comment.id)
        )
        user_likes_comment = self.session.scalar(get_like_query)

        if user_likes_comment is None :
            user_likes_comment = UserLikesComment(
                user_id=user_id,
                comment_id=comment.id,
            )
            self.session.add(user_likes_comment)

            comment.likes_count += 1

        else :
            self.session.delete(user_likes_comment)

            comment.likes_count -= 1
            
        self.session.flush()

        return comment

    def delete_comment_by_id(self, comment: Comment) -> None:
        self.session.delete(comment)
        self.session.flush()