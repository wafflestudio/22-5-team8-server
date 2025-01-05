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
    
    def add_participant_with_movie(self, name: str, profile_url: str | None, role: str, movie: Movie) -> MovieParticipant:
        # 프로필 이미지 없는 동명이인-> 불허
        if self.get_participant(name, profile_url):
            raise ParticipantAlreadyExistsError()
        participant = Participant(name=name, profile_url=profile_url)
        self.session.add(participant)
        self.session.flush()
        
        movie_participant = MovieParticipant(movie_id=movie.id, participant_id=participant.id, role=role)
        self.session.add(movie_participant)
        self.session.flush()
        return movie_participant
    
    def get_participant(self, name: str, profile_url: str | None) -> Participant | None:
        get_participant_query =  select(Participant).filter(
            (Participant.profile_url == profile_url) 
            & (Participant.name == name)
        )
        return self.session.scalar(get_participant_query)
        
    
    def update_participant(self, biography: str) -> None:
        ...