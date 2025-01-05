from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from watchapedia.database.common import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from watchapedia.app.movie.models import Movie, MovieParticipant

class Participant(Base):
    __tablename__ = "participant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    profile_url: Mapped[str | None] = mapped_column(String(500))
    biography: Mapped[str | None] = mapped_column(String(500), default=None)

    movie_participants: Mapped[list["MovieParticipant"]] = relationship("MovieParticipant", back_populates="participant")

