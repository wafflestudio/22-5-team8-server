from sqlalchemy import Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from watchapedia.database.common import Base
from sqlalchemy import DateTime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from watchapedia.app.movie.models import Movie
    from watchapedia.app.user.models import User

class MovieCollection(Base):
    __tablename__ = 'movie_collection'

    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movie.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    collection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collection.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )

class CollectionComment(Base):
    __tablename__ = 'collection_comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="collection_comments")

    collection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collection.id", ondelete="CASCADE"), nullable=False
    )
    collection: Mapped["Collection"] = relationship("Collection", back_populates="comments")

class Collection(Base):
    __tablename__ = 'collection'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    overview: Mapped[str | None] = mapped_column(String(500))
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="collections")
    
    movies: Mapped[list["Movie"]] = relationship(
        secondary="movie_collection", back_populates="collections", cascade="all, delete"
    )
    comments: Mapped[list["CollectionComment"]] = relationship(
        "CollectionComment", back_populates="collection", cascade="all, delete, delete-orphan"
    )

class UserLikesCollection(Base):
    __tablename__ = 'user_likes_collection'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    collection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collection.id", ondelete="CASCADE"), nullable=False
    )

class UserLikesCollectionComment(Base):
    __tablename__ = 'user_likes_collection_comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    collection_comment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collection_comment.id", ondelete="CASCADE"), nullable=False
    )
