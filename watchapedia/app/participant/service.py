from typing import Annotated
from fastapi import Depends
from watchapedia.app.participant.repository import ParticipantRepository
from watchapedia.app.participant.errors import ParticipantNotFoundError
from watchapedia.app.participant.dto.responses import ParticipantDataResponse, MovieDataResponse
from watchapedia.app.movie.models import Movie

class ParticipantService():
    def __init__(self,
                 participant_repository: Annotated[ParticipantRepository, Depends()]
    ):
        self.participant_repository = participant_repository

    def get_participant_information(self, participant_id: int) -> list[ParticipantDataResponse]:
        participant = self.participant_repository.get_participant_by_id(participant_id)
        if participant is None:
            raise ParticipantNotFoundError()
        participant_info = {}
        roles = self.get_participant_roles(participant_id)
        print(roles)
        for role in roles:
            cast = role.split("|")[0].strip()
            movies = self.participant_repository.get_participant_movies(participant_id, cast)
            participant_info[cast] = self._process_movies(movies)
        return [self._process_participants(cast=cast, movies=movies) for cast, movies in participant_info.items()]

        
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