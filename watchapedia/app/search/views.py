from typing import Annotated
from fastapi import APIRouter, Depends

from watchapedia.app.search.service import SearchService
from watchapedia.app.search.dto.responses import SearchResponse
from watchapedia.app.search.dto.requests import validate_search_query

search_router = APIRouter()

@search_router.get("", status_code=200, summary="검색", description="검색어와 일치하는 movie, user, participant, collection, genre id 반환")
def search(
        search_service: Annotated[SearchService, Depends()],
        search_q: str = Depends(validate_search_query),
        begin: int | None = None,
        end: int | None = None,
        ) -> SearchResponse:
    search_service.search(search_q)
    search_service.search_genre(search_q)
    return search_service.process_search_response(begin, end)

