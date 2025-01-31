from typing import Annotated
from fastapi import Depends
from watchapedia.app.calendar.repository import CalendarRepository

class CalendarService():
    def __init__(self,
            calendar_repository: Annotated[CalendarRepository, Depends()]
            ) -> None:
        self.calendar_repository = calendar_repository
        return

    def get_movie_id_by_date(
            self,
            user_id: int, 
            calendar_q1: str, 
            calendar_q2: str
            ) -> dict[str, list[int]]:
        return self.calendar_repository.get_movie_id_by_date(user_id, calendar_q1, calendar_q2)
