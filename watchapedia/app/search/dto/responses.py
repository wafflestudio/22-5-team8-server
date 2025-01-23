from pydantic import BaseModel
# from watchapedia.app.movie.dto.responses import MovieDataResponse
from watchapedia.app.user.dto.responses import UserResponse

class SearchResponse(BaseModel):
    # movie_list: list[MovieDataResponse]
    #user_list: list[UserResponse]
    movie_list: list[int] | None
    user_list: list[int] | None
    participant_list: list[int] | None
    collection_list: list[int] | None

