from sqlalchemy import select, distinct
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from watchapedia.app.participant.models import Participant
from watchapedia.app.movie.models import Movie, MovieParticipant
from watchapedia.app.participant.errors import ParticipantAlreadyExistsError
from typing import Annotated

class ParticipantRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session
    
    def add_participant(self, name: str, profile_url: str | None) -> Participant:
        # 프로필 이미지 없는 동명이인-> 불허
        if self.get_participant(name, profile_url):
            raise ParticipantAlreadyExistsError()
        participant = Participant(name=name, profile_url=profile_url)
        self.session.add(participant)
        self.session.flush()
        return participant
    
    def add_participant_with_movie(self, name: str, profile_url: str | None, role: str, movie: Movie) -> None:
        # 프로필 이미지 없는 동명이인-> 불허
        participant = self.get_participant(name, profile_url)
        if not participant:
            participant = Participant(name=name, profile_url=profile_url)
            self.session.add(participant)
            self.session.flush()

        # MovieParticipant가 중복되는 경우가 존재
        movie_participant = self.get_movie_participant(movie.id, participant.id)
        if not movie_participant:
            movie_participant = MovieParticipant(movie_id=movie.id, participant_id=participant.id, role=role)
            self.session.add(movie_participant)
            self.session.flush()
    
    def get_participant(self, name: str, profile_url: str | None) -> Participant | None:
        get_participant_query =  select(Participant).filter(
            (Participant.profile_url == profile_url) 
            & (Participant.name == name)
        )
        return self.session.scalar(get_participant_query)

    # name으로 복수의 participant get. 부분집합 허용.
    def search_participant_list(self, name: str) -> list[Participant] | None:
        get_participant_query = select(Participant).filter(Participant.name.ilike(f"%{name}%"))
        return self.session.execute(get_participant_query).scalars().all()

    def get_participant_by_id(self, participant_id: int) -> Participant | None:
        get_participant_query = select(Participant).filter(Participant.id == participant_id)
        return self.session.scalar(get_participant_query)
    
    def get_movie_participant(self, movie_id: int, participant_id: int) -> MovieParticipant | None:
        get_movie_participant_query = select(MovieParticipant).filter(
            (MovieParticipant.movie_id == movie_id)
            & (MovieParticipant.participant_id == participant_id)
        )
        return self.session.scalar(get_movie_participant_query)
        
    
    def update_participant(self, participant: Participant, name: str | None, profile_url : str | None, biography: str | None ) -> None:
        if name:
            participant.name = name
        if profile_url:
            participant.profile_url = profile_url
        if biography:
            participant.biography = biography
        self.session.flush()

    def get_participant_roles(self, participant_id: int) -> list[str]:
        get_participant_roles_query = select(distinct(MovieParticipant.role)).filter(
            MovieParticipant.participant_id == participant_id
        )
        return self.session.scalars(get_participant_roles_query).all()
    
    def get_participant_movies(self, participant_id: int, cast: str) -> list[Movie]:
        get_participant_movies_query = select(Movie).join(MovieParticipant).filter(
            (MovieParticipant.participant_id == participant_id)
            & (MovieParticipant.role.contains(cast))
        )
        return self.session.scalars(get_participant_movies_query).all()
