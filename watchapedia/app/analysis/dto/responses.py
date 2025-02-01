from pydantic import BaseModel
from collections import OrderedDict

class UserRatingResponse(BaseModel):
    id: int
    user_id: int
    rating_num: int
    rating_avg: float | None
    rating_dist: dict[float, int]
    rating_mode: float | None
    rating_message: str | None
    viewing_time: int | None
    viewing_message: str | None

class UserPreferenceResponse(BaseModel):
    id: int
    user_id: int
    actor_dict: OrderedDict[int, tuple[float, int]] | None
    director_dict: OrderedDict[int, tuple[float, int]] | None
    country_dict: OrderedDict[int, tuple[float, int]] | None
    genre_dict: OrderedDict[int, tuple[float, int]] | None
