from sqlalchemy import select
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
    
    def get_movie_participant(self, movie_id: int, participant_id: int) -> MovieParticipant | None:
        get_movie_participant_query = select(MovieParticipant).filter(
            (MovieParticipant.movie_id == movie_id)
            & (MovieParticipant.participant_id == participant_id)
        )
        return self.session.scalar(get_movie_participant_query)
        
    
    def update_participant(self, biography: str) -> None:
        ...