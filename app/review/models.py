from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from database.common import Base
from sqlalchemy import DateTime
from app.movie.models import Movie
from app.user.models import User

class Review(Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    content: Mapped[str | None] = mapped_column(String(500))
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    movie_id: Mapped[int] = mapped_column(ForeignKey("movie.id"), nullable=False)
    movie: Mapped["Movie"] = relationship(back_populates="reviews")

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="reviews")