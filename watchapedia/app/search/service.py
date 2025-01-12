from typing import Annotated
from fastapi import Depends
from watchapedia.app.movie.service import MovieService
from watchapedia.app.search.dto.responses import SearchResponse
from watchapedia.app.user.service import UserService

class SearchService():
    def __init__(self,
            movie_service: Annotated[MovieService, Depends()],
            user_service: Annotated[UserService, Depends()]
            ) -> None:
        self.movie_service = movie_service
        self.user_service = user_service

    def search_movie(self,
            title: str
            ) -> None:
        self.movie_list = self.movie_service.search_movie_list(title)
    
    def search_user(self,
            username: str
            ) -> None:
        self.user_list = self.user_service.search_user_list(username)


    def process_search_response(self) -> SearchResponse:
        movie_list = self.movie_list
        user_list = self.user_list

        #if movie_list is None:
        #    raise MovieNotFoundError()

        return SearchResponse(
                movie_list=movie_list,
                user_list=user_list
                )

