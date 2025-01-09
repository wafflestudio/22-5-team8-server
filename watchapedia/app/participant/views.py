from typing import Annotated
from fastapi import APIRouter, Depends
from watchapedia.app.participant.service import ParticipantService
from watchapedia.app.participant.dto.responses import ParticipantDataResponse

participant_router = APIRouter()

@participant_router.get('/{participant_id}',
                    status_code=200, 
                    summary="인물 정보 출력", 
                    description="인물 id를 받아 해당 인물의 정보를 반환합니다.",
                    response_model=list[ParticipantDataResponse]
                    )
def get_participant_information(
    participant_id: int,
    participant_service: Annotated[ParticipantService, Depends()],
) -> list[ParticipantDataResponse]:
    return participant_service.get_participant_information(participant_id)