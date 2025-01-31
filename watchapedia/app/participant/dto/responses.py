from pydantic import BaseModel
from watchapedia.app.participant.models import Participant

class MovieDataResponse(BaseModel):
    id: int
    title: str
    year: int
    average_rating: float | None
    poster_url: str | None
    cast : str | None


class ParticipantDataResponse(BaseModel):
    role: str
    movies: list[MovieDataResponse]

class ParticipantProfileResponse(BaseModel):
    id: int
    name: str
    profile_url: str | None
    roles: list[str]
    biography: str | None
    likes_count: int

    @staticmethod
    def from_entity(participant: Participant, roles: list[str]) -> "ParticipantProfileResponse":
        return ParticipantProfileResponse(
            id=participant.id,
            name=participant.name,
            profile_url=participant.profile_url,
            roles=roles,
            biography=participant.biography,
            likes_count=participant.likes_count
        )