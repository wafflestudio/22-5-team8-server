from typing import Annotated
from fastapi import APIRouter, Depends
from watchapedia.app.participant.service import ParticipantService
from watchapedia.app.participant.dto.requests import ParticipantProfileUpdateRequest
from watchapedia.app.participant.dto.responses import ParticipantDataResponse, ParticipantProfileResponse

participant_router = APIRouter()

@participant_router.get('/{participant_id}',
                    status_code=200, 
                    summary="인물 프로필 출력", 
                    description="인물 id를 받아 해당 인물의 정보(이름, 프로필 url, 역할, 바이오그래피)를 반환합니다.",
                    response_model=ParticipantProfileResponse
                    )

def get_participant_profile(
    participant_id: int,
    participant_service: Annotated[ParticipantService, Depends()],
) -> ParticipantProfileResponse:
    profile, roles = participant_service.get_participant_profile(participant_id)
    return ParticipantProfileResponse.from_entity(profile, roles)

@participant_router.get('/{participant_id}/movies',
                    status_code=200, 
                    summary="인물과 관련된 영화 출력", 
                    description="인물 id를 받아 해당 인물과 관련된 영화들의 정보를 반환합니다.",
                    response_model=list[ParticipantDataResponse]
                    )
def get_participant_movie(
    participant_id: int,
    participant_service: Annotated[ParticipantService, Depends()],
) -> list[ParticipantDataResponse]:
    return participant_service.get_participant_movies(participant_id)


@participant_router.patch('/{participant_id}',
                    status_code=200, 
                    summary="인물 정보 수정", 
                    description="인물 id를 받아 해당 인물의 정보(이름, 프로필 url, 바이오그래피)를 수정합니다.",
                    )
def update_participant_profile(
    participant_id: int,
    participant_service: Annotated[ParticipantService, Depends()],
    profile: ParticipantProfileUpdateRequest
):
    participant_service.update_participant(
        participant_id,
        profile.name,
        profile.profile_url,
        profile.biography
        
    )

    return "Success"