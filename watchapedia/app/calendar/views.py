from typing import Annotated
from fastapi import APIRouter, Depends, Query

from watchapedia.app.calendar.service import CalendarService
from watchapedia.app.calendar.dto.responses import CalendarResponse
from watchapedia.app.calendar.dto.requests import validate_calendar_query

calendar_router = APIRouter()

@calendar_router.get("/{user_id}", status_code=200, summary="캘린더", description="쿼리 기간 사이 날짜별 본 영화 id 반환")
def calendar(
        user_id: int,
        calendar_service: Annotated[CalendarService, Depends()],
        calendar_q1: Annotated[str, Query(..., description="조회 시작일 (YYYY-MM-DD)")],
        calendar_q2: Annotated[str, Query(..., description="조회 종료일 (YYYY-MM-DD)")]
        ) -> CalendarResponse:
    
    start_date = validate_calendar_query(calendar_q1)
    end_date = validate_calendar_query(calendar_q2)

    movie_dict=calendar_service.get_movie_id_by_date(user_id, start_date, end_date)
    return CalendarResponse(
            movie_dict=movie_dict
            )
