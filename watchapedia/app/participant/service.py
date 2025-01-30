from typing import Annotated
from fastapi import Depends
from watchapedia.app.participant.repository import ParticipantRepository
from watchapedia.app.participant.errors import ParticipantNotFoundError
from watchapedia.common.errors import InvalidFormatError, InvalidRangeError
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
        if participant is None:
            raise ParticipantNotFoundError()
        return self._process_participant(participant)

    def get_participant_movies(self, participant_id: int, begin: int | None, end: int | None) -> list[ParticipantDataResponse]:
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
        # pagination
        participant_info["감독"] = self._process_range(participant_info["감독"], begin, end)
        participant_info["출연"] = self._process_range(participant_info["출연"], begin, end)
        return [self._process_participants(role=cast, movies=movies) for cast, movies in participant_info.items()]

    
    def update_participant(self, participant_id: int, name: str | None, profile_url: str | None, biography: str | None):
        participant = self.participant_repository.get_participant_by_id(participant_id)
        if participant is None:
            raise ParticipantNotFoundError()
        if not any([name, profile_url, biography]):
            raise InvalidFormatError()
        self.participant_repository.update_participant(participant, name, profile_url, biography)

    def like_participant(self, user_id: int, participant_id: int) -> ParticipantProfileResponse:
        participant = self.participant_repository.get_participant_by_id(participant_id)
        if participant is None:
            raise ParticipantNotFoundError()
        updated_participant = self.participant_repository.like_participant(user_id, participant)
        return self._process_participant(updated_participant)
    
    def get_like_participant_list(self, user_id: int) -> list[ParticipantProfileResponse]:
        participants = self.participant_repository.get_like_participant_list(user_id)
        return [self._process_participant(participant) for participant in participants]

    def get_participant_roles(self, participant_id: int):
        return self.participant_repository.get_participant_roles(participant_id)
    
    def _process_participant_roles(self, participant_id: int) -> list[str]:
        roles = set()
        full_name_roles = self.get_participant_roles(participant_id)
        for role in full_name_roles:
            if "감독" in role:
                roles.add("감독")
            elif "주연"  in role or "조연" in role or "단역" in role:
                roles.add("배우")
        return list(roles)
    
    def search_participant_list(self, name: str) -> list[ParticipantProfileResponse] | None:
        participants = self.participant_repository.search_participant_list(name)
        return [ParticipantProfileResponse(
                id=participant.id,
                name=participant.name,
                profile_url=None,
                roles=['temp'],
                biography=None) for participant in participants]

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

    def _process_participant(self, participant: Participant) -> ParticipantProfileResponse:
        return ParticipantProfileResponse(
            id=participant.id,
            name=participant.name,
            profile_url=participant.profile_url,
            roles=self._process_participant_roles(participant.id),
            biography=participant.biography,
            likes_count=participant.likes_count
        )
    
    def _process_range(self, response_list, begin: int | None, end: int | None) -> list[MovieDataResponse]:
        if begin is None :
            begin = 0
        if end is None or end > len(response_list) :
            end = len(response_list)
        if begin > len(response_list) :
            begin = len(response_list)
        if begin < 0 or begin > end :
            raise InvalidRangeError()
        return response_list[begin : end]
