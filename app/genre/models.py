from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.common import Base
from app.movie.models import Movie

class MovieGenre(Base):
    __tablename__ = "movie_genre"

    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movie.id"), nullable=False, primary_key=True)
    genre_id: Mapped[int] = mapped_column(Integer, ForeignKey("genre.id"), nullable=False, primary_key=True)

class Genre(Base):
    __tablename__ = "genre"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    movies: Mapped[list["Movie"]] = relationship(secondary="movie_genre", back_populates="genres")
