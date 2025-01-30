from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from typing import Annotated, Sequence
from datetime import datetime
from watchapedia.app.collection_comment.models import CollectionComment, UserLikesCollectionComment
from watchapedia.app.comment.errors import CommentNotFoundError

class CollectionCommentRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def get_comment_by_user_and_collection(self, user_id: int, collection_id: int) -> CollectionComment | None:
        get_comment_query = select(CollectionComment).filter(
            (CollectionComment.user_id == user_id)
            & (CollectionComment.collection_id == collection_id)
        )

        return self.session.scalar(get_comment_query)

    def create_comment(self, user_id: int, collection_id: int, content: str, created_at) -> CollectionComment:
        comment = CollectionComment(
            user_id=user_id,
            collection_id=collection_id,
            content=content,
            likes_count=0,
            created_at=created_at
        )
        self.session.add(comment)
        self.session.flush()

        comment = self.get_comment_by_user_and_collection(user_id, collection_id)

        return comment

    def update_comment(self, comment: CollectionComment, content: str) -> CollectionComment:
        comment.content = content
        self.session.flush()

        return comment

    def get_comments(self, collection_id: int) -> Sequence[CollectionComment]:
        comments_list_query = select(CollectionComment).where(CollectionComment.collection_id == collection_id)
        return self.session.scalars(comments_list_query).all()

    def get_comment_by_comment_id(self, comment_id: int) -> CollectionComment:
        comment = self.session.get(CollectionComment, comment_id)
        if comment is None :
            raise CommentNotFoundError()

        return comment

    def like_comment(self, user_id: int, comment: CollectionComment) -> CollectionComment:
        get_like_query = select(UserLikesCollectionComment).filter(
            (UserLikesCollectionComment.user_id == user_id)
            & (UserLikesCollectionComment.collection_comment_id == comment.id)
        )
        user_likes_comment = self.session.scalar(get_like_query)

        if user_likes_comment is None :
            user_likes_comment = UserLikesCollectionComment(
                user_id=user_id,
                collection_comment_id=comment.id,
            )
            self.session.add(user_likes_comment)

            comment.likes_count += 1

        else :
            self.session.delete(user_likes_comment)

            comment.likes_count -= 1
            
        self.session.flush()

        return comment
    
    def delete_comment_by_id(self, comment: CollectionComment) -> None:
        self.session.delete(comment)
        self.session.flush()

    def like_info(self, user_id: int, comment: CollectionComment) -> bool:
        get_like_query = select(UserLikesCollectionComment).filter(
            (UserLikesCollectionComment.user_id == user_id)
            & (UserLikesCollectionComment.collection_comment_id == comment.id)
        )
        user_likes_comment = self.session.scalar(get_like_query)

        return user_likes_comment is not None