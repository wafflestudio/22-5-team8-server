from typing import Annotated
from fastapi import APIRouter, Depends
from watchapedia.app.participant.service import ParticipantService
from watchapedia.app.participant.dto.requests import ParticipantProfileUpdateRequest
from watchapedia.app.participant.dto.responses import ParticipantDataResponse, ParticipantProfileResponse
from watchapedia.app.user.views import login_with_header
from watchapedia.app.user.models import User

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
    return participant_service.get_participant_profile(participant_id)

@participant_router.get('/{participant_id}/movies',
                    status_code=200, 
                    summary="인물과 관련된 영화 출력", 
                    description="인물 id를 받아 해당 인물과 관련된 영화들의 정보를 개봉연도가 높은 순서로로 반환합니다.",
                    response_model=list[ParticipantDataResponse]
                    )
def get_participant_movie(
    participant_id: int,
    participant_service: Annotated[ParticipantService, Depends()],
    begin: int | None = None,
    end: int | None = None,
) -> list[ParticipantDataResponse]:
    return participant_service.get_participant_movies(participant_id, begin, end)


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

@participant_router.patch('/like/{participant_id}',
                          status_code=200, 
                    summary="인물 추천/취소", 
                    description="인물 id를 받아 추천되어 있지 않으면 추천하고, 추천되어 있으면 취소합니다",
                    )
def like_participant(
    user: Annotated[User, Depends(login_with_header)],
    participant_id: int,
    participant_service: Annotated[ParticipantService, Depends()],
):
    return participant_service.like_participant(user.id, participant_id)