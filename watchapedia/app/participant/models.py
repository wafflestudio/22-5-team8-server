from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from watchapedia.database.common import Base
from watchapedia.app.movie.models import Movie

class Participant(Base):
    __tablename__ = "participant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gender: Mapped[int] = mapped_column(Integer, nullable=False) # 1: male, 2: female
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    movies: Mapped[list["Movie"]] = relationship(secondary="movie_participant", back_populates="participants")

