from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from watchapedia.database.common import Base
from watchapedia.app.movie.models import Movie

class MovieCountry(Base):
    __tablename__ = "movie_country"

    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movie.id"), nullable=False, primary_key=True)
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("country.id"), nullable=False, primary_key=True)

class Country(Base):
    __tablename__ = "country"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    movies: Mapped[list["Movie"]] = relationship(secondary="movie_country", back_populates="countries")
