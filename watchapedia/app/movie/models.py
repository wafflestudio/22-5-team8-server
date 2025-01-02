from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.common import Base
from watchapedia.app.review.models import Review
from watchapedia.app.genre.models import Genre
from watchapedia.app.country.models import Country
from watchapedia.app.participant.models import Participant

class MovieParticipant(Base):
    __tablename__ = "movie_participant"

    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movie.id"), nullable=False, primary_key=True)
    participant_id: Mapped[int] = mapped_column(Integer, ForeignKey("participant.id"), nullable=False, primary_key=True)

    role: Mapped[str] = mapped_column(String(50), nullable=False)


class Movie(Base):
    __tablename__ = "movie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    synopsis: Mapped[str] = mapped_column(String(500), nullable=False, default="등록된 소개글이 없습니다.")
    average_rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    running_time: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)
    poster_url: Mapped[str] = mapped_column(String(200), nullable=False)
    backdrop_url: Mapped[str] = mapped_column(String(200), nullable=False)

    reviews: Mapped[list["Review"]] = relationship(back_populates="movie")
    
    genres: Mapped[list["Genre"]] = relationship(secondary="movie_genre", back_populates="movies")
    countries: Mapped[list["Country"]] = relationship(secondary="movie_country", back_populates="movies")

    movie_participants: Mapped[list[MovieParticipant]] = relationship(MovieParticipant) # movie checks role
    participants: Mapped[list["Participant"]] = relationship(secondary="movie_participant", back_populates="movies")
