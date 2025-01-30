from typing import Annotated
from fastapi import Depends
from watchapedia.common.errors import PermissionDeniedError
from watchapedia.app.collection.repository import CollectionRepository
from watchapedia.app.collection.errors import CollectionNotFoundError
from watchapedia.app.collection_comment.dto.responses import CollectionCommentResponse
from watchapedia.app.collection_comment.repository import CollectionCommentRepository
from watchapedia.app.collection_comment.models import CollectionComment
from watchapedia.app.user.models import User
from watchapedia.app.comment.errors import RedundantCommentError, CommentNotFoundError
from datetime import datetime

class CollectionCommentService:
    def __init__(self,
    collection_repository: Annotated[CollectionRepository, Depends()],
    collection_comment_repository: Annotated[CollectionCommentRepository, Depends()]
    ) -> None:
        self.collection_repository = collection_repository
        self.collection_comment_repository = collection_comment_repository

    def create_comment(self, user_id: int, collection_id: int, content: str) -> CollectionCommentResponse:
        collection = self.collection_repository.get_collection_by_collection_id(collection_id)
        if collection is None :
            raise CollectionNotFoundError()

        new_comment = self.collection_comment_repository.create_comment(user_id=user_id, collection_id=collection_id,
                                                    content=content, created_at=datetime.now())

        return self._process_comment_response(new_comment)

    def update_comment(self, user_id: int, comment_id: int, content: str) -> CollectionCommentResponse:
        comment = self.collection_comment_repository.get_comment_by_comment_id(comment_id)
        if not comment.user_id == user_id :
            raise PermissionDeniedError()

        updated_comment = self.collection_comment_repository.update_comment(comment, content=content)
        return self._process_comment_response(updated_comment)

    def list_comments(self, collection_id: int) -> list[CollectionCommentResponse]:
        collection = self.collection_repository.get_collection_by_collection_id(collection_id)
        if collection is None :
            raise CollectionNotFoundError()

        comments = self.collection_comment_repository.get_comments(collection_id)
        return [self._process_comment_response(comment) for comment in comments]

    def like_comment(self, user_id: int, comment_id: int) -> CollectionCommentResponse :
        comment = self.collection_comment_repository.get_comment_by_comment_id(comment_id)
        if comment is None :
            raise CommentNotFoundError()

        updated_comment = self.collection_comment_repository.like_comment(user_id, comment)
        return self._process_comment_response(updated_comment)
    
    def delete_comment_by_id(self, comment_id: int, user: User) -> None:
        comment = self.collection_comment_repository.get_comment_by_comment_id(comment_id)
        if comment is None:
            raise CommentNotFoundError()
        if comment.user_id != user.id:
            raise PermissionDeniedError()
        self.collection_comment_repository.delete_comment_by_id(comment)

    def like_info(self, user_id: int, comment_id: int) -> bool :
        comment = self.collection_comment_repository.get_comment_by_comment_id(comment_id)
        if comment is None :
            raise CommentNotFoundError()
        return self.collection_comment_repository.like_info(user_id, comment)

    def _process_comment_response(self, comment: CollectionComment) -> CollectionCommentResponse:
        return CollectionCommentResponse(
            id=comment.id,
            user_id=comment.user.id,
            user_name=comment.user.username,
            profile_url=comment.user.profile_url,
            collection_id=comment.collection_id,
            content=comment.content,
            likes_count=comment.likes_count,
            created_at=comment.created_at
        )
