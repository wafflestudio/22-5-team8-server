from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from typing import Annotated, Sequence
from watchapedia.app.movie.models import Movie
from watchapedia.app.collection.models import Collection, UserLikesCollection, UserLikesCollectionComment
from watchapedia.app.collection.errors import CollectionNotFoundError
from datetime import datetime

class CollectionRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def create_collection(
            self, user_id: int, title: str, overview: str | None, created_at: datetime
    ) -> Collection:
        collection = Collection(
            user_id=user_id,
            title=title,
            overview=overview,
            likes_count=0,
            created_at=created_at
        )
        self.session.add(collection)
        self.session.flush()

        return collection

    def add_collection_movie(
            self, collection: Collection, movies: list[Movie]
    ) -> None:
        for movie in movies:
            collection.movies.append(movie)

        self.session.flush()

    def update_collection(
            self, collection: Collection, title: str | None, overview: str | None, add_movie_ids: list[int] | None, delete_movie_ids: list[int] | None
    ) -> None:
        if title:
            collection.title = title

        if overview:
            collection.overview = overview
        
        if delete_movie_ids:
            for delete_movie_id in delete_movie_ids:
                delete_movie = self.get_movie_by_movie_id(delete_movie_id)
                collection.movies.remove(delete_movie)

        if add_movie_ids:
            for add_movie_id in add_movie_ids:
                add_movie = self.get_movie_by_movie_id(add_movie_id)
                collection.movies.append(add_movie)

        self.session.flush()

    def like_collection(self, user_id: int, collection: Collection) -> Collection:
        get_like_query = select(UserLikesCollection).filter(
            (UserLikesCollection.user_id == user_id)
            & (UserLikesCollection.collection_id == collection.id)
        )
        user_likes_collection = self.session.scalar(get_like_query)

        if user_likes_collection is None:
            user_likes_collection = UserLikesCollection(
                user_id=user_id,
                collection_id=collection.id
            )
            self.session.add(user_likes_collection)
            collection.likes_count += 1
        else:
            self.session.delete(user_likes_collection)
            collection.likes_count -= 1
        self.session.flush()
        return collection

    def get_collections_by_user_id(self, user_id: int) -> Sequence[Collection]:
        collections_list_query = select(Collection).where(Collection.user_id == user_id)
        return self.session.scalars(collections_list_query).all()

    def get_collection_by_collection_id(self, collection_id: int) -> Collection | None:
        get_collection_query = select(Collection).filter(Collection.id == collection_id)
        return self.session.scalar(get_collection_query)
    
    def get_movie_by_movie_id(self, movie_id: int) -> Movie | None:
        get_movie_query = select(Movie).filter(Movie.id==movie_id)
        return self.session.scalar(get_movie_query)
    
    def delete_collection_by_id(self, collection: Collection) -> None:
        self.session.delete(collection)
        self.session.flush()
