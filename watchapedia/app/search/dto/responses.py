from pydantic import BaseModel
from watchapedia.app.movie.dto.responses import MovieDataResponse
from watchapedia.app.user.dto.responses import UserResponse

class SearchResponse(BaseModel):
    movie_list: list[MovieDataResponse]
    user_list: list[UserResponse]

