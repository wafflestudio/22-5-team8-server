from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from typing import Annotated, Sequence
from watchapedia.app.movie.models import Movie
from watchapedia.app.collection.models import Collection, UserLikesCollectionComment
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

    def get_collection_by_collection_id(self, collection_id: int) -> Collection | None:
        get_collection_query = select(Collection).filter(Collection.id == collection_id)
        return self.session.scalar(get_collection_query)
