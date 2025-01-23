from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from watchapedia.database.common import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from watchapedia.app.review.models import Review
    from watchapedia.app.genre.models import Genre
    from watchapedia.app.country.models import Country
    from watchapedia.app.participant.models import Participant
    from watchapedia.app.collection.models import Collection

class MovieParticipant(Base):
    __tablename__ = "movie_participant"

    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movie.id"), nullable=False, primary_key=True)
    participant_id: Mapped[int] = mapped_column(Integer, ForeignKey("participant.id"), nullable=False, primary_key=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    
    movie: Mapped["Movie"] = relationship("Movie", back_populates="movie_participants")
    participant: Mapped["Participant"] = relationship("Participant", back_populates="movie_participants")

class Chart(Base):
    __tablename__ = "chart"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movie.id"), nullable=False)
    movie: Mapped["Movie"] = relationship("Movie", back_populates="charts")
    
class Movie(Base):
    __tablename__ = "movie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    original_title: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    synopsis: Mapped[str] = mapped_column(String(1000), nullable=False, default="등록된 소개글이 없습니다.")
    average_rating: Mapped[float | None] = mapped_column(Float, default=None)
    running_time: Mapped[int | None] = mapped_column(Integer)
    grade: Mapped[str | None] = mapped_column(String(20))
    poster_url: Mapped[str | None] = mapped_column(String(500))
    backdrop_url: Mapped[str | None] = mapped_column(String(500))

    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="movie")
    
    genres: Mapped[list["Genre"]] = relationship(secondary="movie_genre", back_populates="movies")
    countries: Mapped[list["Country"]] = relationship(secondary="movie_country", back_populates="movies")
    collections: Mapped[list["Collection"]] = relationship(secondary="movie_collection", back_populates="movies")

    movie_participants: Mapped[list[MovieParticipant]] = relationship("MovieParticipant", back_populates="movie")
    
    charts: Mapped[list["Chart"]] = relationship("Chart", back_populates="movie")
