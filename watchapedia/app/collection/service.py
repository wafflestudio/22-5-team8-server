from typing import Annotated
from fastapi import Depends
from datetime import datetime
from watchapedia.app.collection.repository import CollectionRepository
from watchapedia.app.collection.models import Collection
from watchapedia.app.collection.dto.responses import CollectionResponse, MovieCompactResponse
from watchapedia.app.movie.repository import MovieRepository
from watchapedia.app.movie.errors import MovieNotFoundError

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
        
        return self._process_collection_process(collection)
    
    def _process_collection_process(self, collection: Collection) -> CollectionResponse:
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