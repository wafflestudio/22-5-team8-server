from typing import Annotated
from fastapi import Depends
from datetime import datetime
from watchapedia.app.collection.repository import CollectionRepository
from watchapedia.app.collection.models import Collection
from watchapedia.app.user.models import User
from watchapedia.app.collection.dto.responses import CollectionResponse, MovieCompactResponse
from watchapedia.app.movie.repository import MovieRepository
from watchapedia.app.movie.errors import MovieNotFoundError
from watchapedia.app.collection.errors import *
from watchapedia.common.errors import PermissionDeniedError

class CollectionService:
    def __init__(
            self, 
            movie_repository: Annotated[MovieRepository, Depends()], 
            collection_repository: Annotated[CollectionRepository, Depends()]
    ) -> None:
        self.movie_repository = movie_repository
        self.collection_repository = collection_repository

    def create_collection(
            self, user_id: int, movie_ids: list[int] | None, title: str, overview: str | None
    ) -> CollectionResponse:
        collection = self.collection_repository.create_collection(
            user_id=user_id, title=title, overview=overview, created_at=datetime.now()
        )
        if movie_ids:
            movies = []
            for movie_id in movie_ids:
                movie = self.movie_repository.get_movie_by_movie_id(movie_id=movie_id)
                if movie is None:
                    raise MovieNotFoundError()
                movies.append(movie)
            self.collection_repository.add_collection_movie(collection=collection, movies=movies)
        
        return self._process_collection_response(collection)
    
    def update_collection(
            self, collection_id: int, user_id: int, title: int | None, overview: int | None, add_movie_ids: list[int] | None, delete_movie_ids: list[int] | None
    ) -> None:
        if not any([title, overview, add_movie_ids, delete_movie_ids]):
            raise InvalidFormatError()
        collection = self.collection_repository.get_collection_by_collection_id(collection_id)
        if not collection.user_id == user_id:
            raise PermissionDeniedError()
        
        movie_id_list = self.get_movie_ids_from_collection(collection_id)
        if delete_movie_ids:
            for delete_movie_id in delete_movie_ids:
                if delete_movie_id not in movie_id_list:
                    raise NoSuchMovieError()
        if add_movie_ids:
            for add_movie_id in add_movie_ids:
                if self.movie_repository.get_movie_by_movie_id(add_movie_id) is None:
                    raise MovieNotFoundError()
                if add_movie_id in movie_id_list:
                    raise MovieAlreadyExistsError()
        
        self.collection_repository.update_collection(
            collection=collection, title=title, overview=overview, add_movie_ids=add_movie_ids, delete_movie_ids=delete_movie_ids
        )

    def get_collection_by_collection_id(self, collection_id: int) -> CollectionResponse:
        collection = self.collection_repository.get_collection_by_collection_id(collection_id=collection_id)
        if collection is None:
            raise CollectionNotFoundError()
        return self._process_collection_response(collection)
    
    def get_movie_ids_from_collection(self, collection_id: int) -> list[int] | None:
        collection = self.collection_repository.get_collection_by_collection_id(collection_id=collection_id)
        if collection is None:
            raise CollectionNotFoundError()
        return [ movie.id for movie in collection.movies ]
    
    def like_collection(self, user_id: int, collection_id: int) -> CollectionResponse:
        collection = self.collection_repository.get_collection_by_collection_id(collection_id)
        updated_collection = self.collection_repository.like_collection(user_id, collection)
        return self._process_collection_response(updated_collection)
    
    def get_user_collections(self, user: User) -> list[CollectionResponse]:
        collections = self.collection_repository.get_collections_by_user_id(user.id)
        return [ self._process_collection_response(collection) for collection in collections ]
    
    def delete_collection_by_id(self, collection_id: int, user: User) -> None:
        collection = self.collection_repository.get_collection_by_collection_id(collection_id)
        if collection is None:
            raise CollectionNotFoundError()
        if collection.user_id != user.id:
            raise PermissionDeniedError()
        self.collection_repository.delete_collection_by_id(collection)
    
    def _process_collection_response(self, collection: Collection) -> CollectionResponse:
        return CollectionResponse(
            id=collection.id,
            user_id=collection.user_id,
            title=collection.title,
            overview=collection.overview,
            likes_count=collection.likes_count,
            comments_count=len(collection.comments),
            created_at=collection.created_at,
            movies=[
                MovieCompactResponse(
                    id=movie.id,
                    title=movie.title,
                    poster_url=movie.poster_url,
                    average_rating=movie.average_rating
                )
                for movie in collection.movies
            ]
        )