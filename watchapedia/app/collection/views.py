from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
from datetime import datetime
from watchapedia.app.user.views import login_with_header
from watchapedia.app.user.models import User
from watchapedia.app.collection.service import CollectionService
from watchapedia.app.collection.dto.requests import CollectionCreateRequest, CollectionUpdateRequest
from watchapedia.app.collection.dto.responses import CollectionResponse

collection_router = APIRouter()

@collection_router.post("",
                    status_code=201,
                    summary="컬렉션 생성",
                    description="[로그인 필요] 컬렉션 title, overview(소개글), movie_ids를 받아 컬랙션을 생성하고 성공 시 컬렉션을 반환합니다."
                )
def create_collection(
    user: Annotated[User, Depends(login_with_header)],
    collection_service: Annotated[CollectionService, Depends()],
    collection_request: CollectionCreateRequest,
) -> CollectionResponse:
    return collection_service.create_collection(
        user.id, collection_request.movie_ids, collection_request.title, collection_request.overview
    )

@collection_router.get("/{collection_id}",
                    status_code=200,
                    summary="컬렉션 조회",
                    description="컬렉션 id로 조회하여 성공 시 컬렉션을 반환합니다."
                )
def search_collection(
    collection_id: int,
    collection_service: Annotated[CollectionService, Depends()],
) -> CollectionResponse:
    return collection_service.get_collection_by_collection_id(collection_id)

@collection_router.patch("/{collection_id}",
                    status_code=200,
                    summary="컬렉션 업데이트",
                    description="[로그인 필요] title, overview(소개글), 추가할 영화 id 목록, 삭제할 영화 id 목록을 받아 성공 시 'Success'을 반환합니다."
                )
def update_collection(
    user: Annotated[User, Depends(login_with_header)],
    collection_id: int,
    collection_request: CollectionUpdateRequest,
    collection_service: Annotated[CollectionService, Depends()]
):
    collection_service.update_collection(
        collection_id, user.id, collection_request.title, collection_request.overview, collection_request.add_movie_ids, collection_request.delete_movie_ids
    )
    return "Success"