from sqlalchemy import Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from watchapedia.database.common import Base
from sqlalchemy import DateTime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from watchapedia.app.movie.models import Movie
    from watchapedia.app.user.models import User

class Review(Base):
    __tablename__ = 'review'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String(500), nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    spoiler: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movie.id"), nullable=False
    )
    movie: Mapped["Movie"] = relationship("Movie", back_populates="reviews")

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="review")

class UserLikesReview(Base):
    __tablename__ = 'user_likes_review'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )
    review_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("review.id"), nullable=False
    )
