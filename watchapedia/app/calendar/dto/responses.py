from pydantic import BaseModel

class CalendarResponse(BaseModel):
    movie_dict: dict[str, list[int]] | None
