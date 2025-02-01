from sqlalchemy import Integer, ForeignKey, Float, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from watchapedia.database.common import Base

class UserRating(Base):
    __tablename__ = 'user_rating'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False, unique=True)
    rating_num: Mapped[int] = mapped_column(Integer, nullable=False)
    rating_avg: Mapped[float] = mapped_column(Float, nullable=True)
    rating_dist: Mapped[dict[float, int]] = mapped_column(JSON, nullable=True)
    rating_mode: Mapped[float] = mapped_column(Float, nullable=True)
    rating_message: Mapped[str] = mapped_column(String(100), nullable=True)
    viewing_time: Mapped[int] = mapped_column(Integer, nullable=True)
    viewing_message: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="user_rating", uselist=False)


class UserPreference(Base):
    __tablename__ = 'user_preference'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False, unique=True)
    actor_dict: Mapped[dict[int, tuple[float, int]]] = mapped_column(JSON, nullable=True)
    director_dict: Mapped[dict[int, tuple[float, int]]] = mapped_column(JSON, nullable=True)
    country_dict: Mapped[dict[int, tuple[float, int]]] = mapped_column(JSON, nullable=True)
    genre_dict: Mapped[dict[int, tuple[float, int]]] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="user_preference", uselist=False)
