from typing import Annotated
from fastapi import Depends
from watchapedia.app.participant.repository import ParticipantRepository
from watchapedia.app.participant.errors import ParticipantNotFoundError
from watchapedia.common.errors import InvalidFormatError
from watchapedia.app.participant.dto.responses import ParticipantDataResponse, MovieDataResponse, ParticipantProfileResponse
from watchapedia.app.movie.models import Movie
from watchapedia.app.participant.models import Participant

class ParticipantService():
    def __init__(self,
                 participant_repository: Annotated[ParticipantRepository, Depends()]
    ):
        self.participant_repository = participant_repository

    def get_participant_profile(self, participant_id: int) -> ParticipantProfileResponse:
        participant = self.participant_repository.get_participant_by_id(participant_id)
        tmp = self.get_participant_roles(participant_id)
        roles = set()
        for role in tmp:
            if role == "감독":
                roles.add("감독")
            elif role == "주연" or role == "조연" or role == "단역":
                roles.add("배우")
        if participant is None:
            raise ParticipantNotFoundError()
        return participant, roles

    def get_participant_movies(self, participant_id: int) -> list[ParticipantDataResponse]:
        participant = self.participant_repository.get_participant_by_id(participant_id)
        if participant is None:
            raise ParticipantNotFoundError()
        participant_info = {}
        roles = self.get_participant_roles(participant_id)
        for role in roles:
            cast = role.split("|")[0].strip()
            movies = self.participant_repository.get_participant_movies(participant_id, cast)
            participant_info[cast] = self._process_movies(movies)
        return [self._process_participants(cast=cast, movies=movies) for cast, movies in participant_info.items()]
    
    def update_participant(self, participant_id: int, name: str | None, profile_url: str | None, biography: str | None):
        participant = self.participant_repository.get_participant_by_id(participant_id)
        if participant is None:
            raise ParticipantNotFoundError()
        if not any([name, profile_url, biography]):
            raise InvalidFormatError()
        self.participant_repository.update_participant(participant, name, profile_url, biography)


        
    def get_participant_roles(self, participant_id: int):
        return self.participant_repository.get_participant_roles(participant_id)

    def _process_movies(self, movies: list[Movie]) -> list[MovieDataResponse]:
        return [MovieDataResponse(id=movie.id, 
                                  title=movie.title, 
                                  year=movie.year, 
                                  average_rating=movie.average_rating, 
                                  poster_url=movie.poster_url) 
                                  for movie in movies]
    
    def _process_participants(self, cast: str, movies: list[MovieDataResponse]) -> ParticipantDataResponse:
        return ParticipantDataResponse(cast=cast, movies=movies)