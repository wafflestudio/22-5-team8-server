from typing import Annotated
from fastapi import APIRouter, Depends

from watchapedia.app.search.service import SearchService
from watchapedia.app.search.dto.requests import SearchRequest
from watchapedia.app.search.dto.responses import SearchResponse

search_router = APIRouter()

@search_router.get("/", status_code=200, summary="검색", description="검색어와 일치하는 영화, 배우, 감독, 컬션렉션 반환")
def search(search_request: SearchRequest,
        search_service: Annotated[SearchService, Depends()]
        ) -> SearchResponse:
    search_q = search_request.search_query
    search_service.search_movie(search_q)
    search_service.search_user(search_q)
    return search_service.process_search_response()
