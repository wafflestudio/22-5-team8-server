from typing import Annotated
from fastapi import APIRouter, Depends

from watchapedia.app.search.service import SearchService
from watchapedia.app.search.dto.requests import SearchRequest
from watchapedia.app.search.dto.responses import SearchResponse

search_router = APIRouter()

@search_router.get("/{search_q}", status_code=200, summary="검색", description="검색어와 일치하는 영화이름 반환")
def search(search_q: str,
        search_service: Annotated[SearchService, Depends()]
        ) -> SearchResponse:
    search_service.search_movie(search_q)
    search_service.search_user(search_q)
    return search_service.process_search_response()
