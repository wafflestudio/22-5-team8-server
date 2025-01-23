from typing import Annotated
from fastapi import Depends
from watchapedia.app.search.dto.responses import SearchResponse
from watchapedia.app.movie.service import MovieService
from watchapedia.app.user.service import UserService
from watchapedia.app.participant.service import ParticipantService
from watchapedia.app.collection.service import CollectionService
from watchapedia.app.genre.repository import GenreRepository

class SearchService():
    def __init__(self,
            movie_service: Annotated[MovieService, Depends()],
            user_service: Annotated[UserService, Depends()],
            participant_service: Annotated[ParticipantService, Depends()],
            collection_service: Annotated[CollectionService, Depends()],
            genre_repository: Annotated[GenreRepository, Depends()]
            ) -> None:
        self.movie_service = movie_service
        self.user_service = user_service
        self.participant_service = participant_service
        self.collection_service = collection_service
        self.genre_repository = genre_repository

    
    def search(self,
            name: str
            ) -> None:
        self.movie_list = self.movie_service.search_movie_list(title=name)
        self.user_list = self.user_service.search_user_list(name)
        self.participant_list = self.participant_service.search_participant_list(name)
        self.collection_list = self.collection_service.search_collection_list(name)

    def search_genre(self,
            name: str
            ) -> None:
        self.genre_list = self.genre_repository.get_genres_by_genre_name(name)
        self.movie_dict_by_genre = {}
        for genre in self.genre_list:
            self.movie_dict_by_genre[genre.name] = self.movie_service.search_movie_list(genres=[genre.name])
        for key in self.movie_dict_by_genre:
            self.movie_dict_by_genre[key] = [movie.id for movie in self.movie_dict_by_genre[key]]

    def process_search_response(self) -> SearchResponse:
        movie_list = [i.id for i in self.movie_list]
        user_list = [i.id for i in self.user_list]
        participant_list = [i.id for i in self.participant_list]
        collection_list = [i.id for i in self.collection_list]
        
        return SearchResponse(
                movie_list=movie_list,
                user_list=user_list,
                participant_list=participant_list,
                collection_list=collection_list,
                movie_dict_by_genre=self.movie_dict_by_genre
                )

