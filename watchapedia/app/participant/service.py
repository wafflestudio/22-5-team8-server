from typing import Annotated
from fastapi import Depends
from watchapedia.app.participant.repository import ParticipantRepository
from watchapedia.app.participant.errors import ParticipantNotFoundError
from watchapedia.common.errors import InvalidFormatError
from watchapedia.app.participant.dto.responses import ParticipantDataResponse, MovieDataResponse, ParticipantProfileResponse
from watchapedia.app.movie.models import Movie
from watchapedia.app.participant.models import Participant
from collections import defaultdict

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
        participant_info = {"감독": [], "출연": []}
        roles = self.get_participant_roles(participant_id)
        casts = set()
        for role in roles:
            casts.add(role.split("|")[0].strip())
        for cast in casts:
            movies = self.participant_repository.get_participant_movies(participant_id, cast)
            if cast == "감독":
                participant_info["감독"].extend(self._process_movies(movies, cast))
            elif cast in ["주연", "조연", "단역"]:
                participant_info["출연"].extend(self._process_movies(movies, cast))
        participant_info["감독"] = sorted(participant_info["감독"], key=lambda x: x.year, reverse=True) # 연도 내림차순 정렬
        participant_info["출연"] = sorted(participant_info["출연"], key=lambda x: x.year, reverse=True) # 연도 내림차순 정렬
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