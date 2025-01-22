from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
from datetime import datetime
from watchapedia.app.user.views import login_with_header
from watchapedia.app.user.models import User
from watchapedia.app.comment.dto.requests import CommentRequest
from watchapedia.app.comment.dto.responses import CommentResponse
from watchapedia.app.comment.models import Comment
from watchapedia.app.comment.service import CommentService
from watchapedia.app.comment.errors import *

comment_router = APIRouter()

@comment_router.post('/{review_id}',
                status_code=201, 
                summary="코멘트 작성", 
                description="review_id, content를 받아 코멘트를 작성하고 성공 시 username을 포함하여 코멘트를 반환합니다.",
            )
def create_comment(
    user: Annotated[User, Depends(login_with_header)],
    comment_service: Annotated[CommentService, Depends()],
    review_id: int,
    comment: CommentRequest,
) -> CommentResponse:
    commentresponse = comment_service.create_comment(user.id, review_id, comment.content)
    return commentresponse

@comment_router.patch('/{comment_id}',
                status_code=200, 
                summary="코멘트 수정", 
                description="comment_id와 content를 받아 코멘트를 수정하고 반환합니다.",
                response_model=CommentResponse
                )
def update_comment(
    user: Annotated[User, Depends(login_with_header)],
    comment_service: Annotated[CommentService, Depends()],
    comment_id: int,
    comment: CommentRequest,
):
    return comment_service.update_comment(
        user.id, comment_id, comment.content
    )

@comment_router.get('/list',
                status_code=200, 
                summary="유저 코멘트 출력", 
                description="유저가 남긴 모든 코멘트들을 반환합니다",
                response_model=list[CommentResponse]
                )
def get_comments_by_user(
    user: Annotated[User, Depends(login_with_header)],
    comment_service: Annotated[CommentService, Depends()],
):
    return comment_service.user_comments(user.id)

@comment_router.get('/{review_id}',
                status_code=200, 
                summary="비로그인 코멘트 출력", 
                description="[로그인 불필요] review_id를 받아 해당 리뷰에 달린 코멘트들을 반환합니다",
                response_model=list[CommentResponse]
                )
def get_comments_by_review(
    review_id: int,
    comment_service: Annotated[CommentService, Depends()],
):
    return comment_service.review_comments(review_id)

@comment_router.get('/list/{review_id}',
                status_code=200, 
                summary="로그인 코멘트 출력", 
                description="[로그인 필요] review_id를 받아 해당 리뷰에 달린 코멘트들을 포함하여 유저가 해당 코멘트들을 추천했는지 반환합니다",
                response_model=list[CommentResponse]
                )
def get_comments_by_review_and_user(
    user: Annotated[User, Depends(login_with_header)],
    review_id: int,
    comment_service: Annotated[CommentService, Depends()],
):
    return comment_service.review_user_comments(user.id, review_id)

@comment_router.patch('/like/{comment_id}',
                status_code=200, 
                summary="코멘트 추천/취소", 
                description="comment_id를 받아 추천되어 있지 않으면 추천하고, 추천되어 있으면 취소합니다.",
                response_model=CommentResponse
            )
def like_comment(
    user: Annotated[User, Depends(login_with_header)],
    comment_id: int,
    comment_service: Annotated[CommentService, Depends()],
):
    return comment_service.like_comment(user.id, comment_id)

@comment_router.delete('/{comment_id}',
                status_code=204,
                summary="코멘트 삭제",
                description="[로그인 필요] 코멘트 id를 받아 해당 코멘트를 삭제합니다. 성공 시 204 code 반환")
def delete_comment(
    user: Annotated[User, Depends(login_with_header)],
    comment_id: int,
    comment_service: Annotated[CommentService, Depends()]
):
    comment_service.delete_comment_by_id(user.id, comment_id)
