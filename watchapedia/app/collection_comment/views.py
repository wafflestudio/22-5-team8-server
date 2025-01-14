from fastapi import APIRouter, Depends
from typing import Annotated
from datetime import datetime
from watchapedia.app.user.views import login_with_header
from watchapedia.app.user.models import User
from watchapedia.app.collection_comment.dto.requests import CollectionCommentRequest
from watchapedia.app.collection_comment.dto.responses import CollectionCommentResponse
from watchapedia.app.collection_comment.models import CollectionComment
from watchapedia.app.collection_comment.service import CollectionCommentService

collection_comment_router = APIRouter()

@collection_comment_router.post('/{collection_id}',
                status_code=201, 
                summary="코멘트 작성", 
                description="[로그인 필요] collection_id, content를 받아 코멘트를 작성하고 성공 시 username을 포함하여 코멘트를 반환합니다.",
            )
def create_comment(
    user: Annotated[User, Depends(login_with_header)],
    collection_comment_service: Annotated[CollectionCommentService, Depends()],
    collection_id: int,
    comment: CollectionCommentRequest,
) -> CollectionCommentResponse:
    commentresponse = collection_comment_service.create_comment(user.id, collection_id, comment.content)
    return commentresponse

@collection_comment_router.patch('/{comment_id}',
                status_code=200, 
                summary="코멘트 수정", 
                description="[로그인 필요] comment_id와 content를 받아 코멘트를 수정하고 반환합니다.",
                )
def update_comment(
    user: Annotated[User, Depends(login_with_header)],
    collection_comment_service: Annotated[CollectionCommentService, Depends()],
    comment_id: int,
    comment: CollectionCommentRequest,
) -> CollectionCommentResponse:
    return collection_comment_service.update_comment(
        user.id, comment_id, comment.content
    )

@collection_comment_router.get('/{collection_id}',
                status_code=200, 
                summary="코멘트 출력", 
                description="collection_id를 받아 해당 리뷰에 달린 코멘트들을 반환합니다",
                )
def get_comments(
    collection_id: int,
    collection_comment_service: Annotated[CollectionCommentService, Depends()],
) -> list[CollectionCommentResponse]:
    return collection_comment_service.list_comments(collection_id)

@collection_comment_router.patch('/like/{comment_id}',
                status_code=200, 
                summary="코멘트 추천/취소", 
                description="[로그인 필요] comment_id를 받아 추천되어 있지 않으면 추천하고, 추천되어 있으면 취소합니다.",
            )
def like_comment(
    user: Annotated[User, Depends(login_with_header)],
    comment_id: int,
    collection_comment_service: Annotated[CollectionCommentService, Depends()],
) -> CollectionCommentResponse:
    return collection_comment_service.like_comment(user.id, comment_id)

@collection_comment_router.delete('/{comment_id}',
                status_code=204,
                summary="코멘트 삭제",
                description="[로그인 필요] 코멘트 id를 받아 해당 코멘트을 삭제합니다. 성공 시 204 code 반환")
def delete_comment(
    collection_id: int,
    user: Annotated[User, Depends(login_with_header)],
    collection_comment_service: Annotated[CollectionCommentService, Depends()]
):
    collection_comment_service.delete_comment_by_id(collection_id, user)