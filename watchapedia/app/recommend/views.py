from typing import Annotated
from fastapi import APIRouter, Depends

from watchapedia.app.user.views import login_with_header
from watchapedia.app.user.models import User
from watchapedia.app.recommend.service import RecommendService
from watchapedia.app.recommend.dto.responses import RecommendResponse

recommend_router = APIRouter()

@recommend_router.get("/expect",
                    status_code=200,
                    summary="예상 평점 기반 추천 영화",
                    description="유저 간의 유사도를 기반으로 계산된 예상 평점이 높은 영화들을 순서대로 최대 5편 추천합니다.",
                    response_model=list[RecommendResponse]
                    )
def high_expected_rating(
    user: Annotated[User, Depends(login_with_header)],
    recommend_service: Annotated[RecommendService, Depends()],
):
    return recommend_service.high_expected_rating(user.id, 5)

@recommend_router.get("/difference",
                    status_code=200,
                    summary="유저 맞춤 추천 영화",
                    description="평균 평점에 비해 예상 평점이 높은 영화들을 순서대로 최대 5편 추천합니다.",
                    response_model=list[RecommendResponse]
                    )
def high_difference(
    user: Annotated[User, Depends(login_with_header)],
    recommend_service: Annotated[RecommendService, Depends()],
):
    return recommend_service.high_difference(user.id, 5)


