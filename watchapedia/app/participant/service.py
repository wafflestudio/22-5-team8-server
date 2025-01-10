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
        # 감독과 배우 구분
        roles = set()
        for role in tmp:
            if "감독" in role:
                roles.add("감독")
            elif "주연"  in role or "조연" in role or "단역" in role:
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
            cast = role.split("|")[0].strip() # role에서 "|"로 구분된 문자열에서 앞에 있는 문자열만 가져옴
            movies = self.participant_repository.get_participant_movies(participant_id, cast)
            if cast == "감독":
                participant_info["감독"] = self._process_movies(movies, cast)
            elif cast == "주연" or cast == "조연" or cast == "단역":
                participant_info["출연"] = self._process_movies(movies, cast)
        return [self._process_participants(role=cast, movies=movies) for cast, movies in participant_info.items()]
    
    def update_participant(self, participant_id: int, name: str | None, profile_url: str | None, biography: str | None):
        participant = self.participant_repository.get_participant_by_id(participant_id)
        if participant is None:
            raise ParticipantNotFoundError()
        if not any([name, profile_url, biography]):
            raise InvalidFormatError()
        self.participant_repository.update_participant(participant, name, profile_url, biography)


        
    def get_participant_roles(self, participant_id: int):
        return self.participant_repository.get_participant_roles(participant_id)

    def _process_movies(self, movies: list[Movie], cast: str) -> list[MovieDataResponse]:
        return [MovieDataResponse(id=movie.id, 
                                  title=movie.title, 
                                  year=movie.year, 
                                  average_rating=movie.average_rating, 
                                  poster_url=movie.poster_url,
                                  cast=cast) 
                                  for movie in movies]
    
    def _process_participants(self, role: str, movies: list[MovieDataResponse]) -> ParticipantDataResponse:
        return ParticipantDataResponse(role=role, movies=movies)