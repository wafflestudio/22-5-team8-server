from typing import Annotated, Union
from fastapi import APIRouter, Depends

from watchapedia.app.analysis.service import UserRatingService
from watchapedia.app.analysis.service import UserPreferenceService
from watchapedia.app.analysis.dto.responses import UserRatingResponse
from watchapedia.app.analysis.dto.responses import UserPreferenceResponse
from watchapedia.app.analysis.dto.requests import validate_analysis_query

from collections import OrderedDict

analysis_router = APIRouter()

@analysis_router.get('/{user_id}', status_code=200, summary="취향분석", description="user preference analysis")
def analysis(
        user_id: int,
        user_rating_service: Annotated[UserRatingService, Depends()],
        user_preference_service: Annotated[UserPreferenceService, Depends()],
        analysis_q: str = Depends(validate_analysis_query)
        ) -> Union[UserRatingResponse, UserPreferenceResponse]:

    if analysis_q == "rating":
        user_rating = user_rating_service.get_user_rating_by_user_id(user_id)
        user_rating_id = user_rating.id
        rating_num = user_rating.rating_num
        rating_avg = user_rating.rating_avg
        rating_dist = user_rating.rating_dist
        rating_mode = user_rating.rating_mode
        rating_message = user_rating.rating_message
        viewing_time = user_rating.viewing_time
        viewing_message = user_rating.viewing_message

        return UserRatingResponse(id=user_rating_id,
            user_id=user_id,
            rating_num=rating_num,
            rating_avg=rating_avg,
            rating_dist=rating_dist, 
            rating_mode=rating_mode,
            rating_message=rating_message,
            viewing_time=viewing_time,
            viewing_message=viewing_message)

    elif analysis_q == "preference":
        user_preference = user_preference_service.get_user_preference_by_user_id(user_id)
        user_preference_id = user_preference.id

        actor_dict = user_preference.actor_dict
        director_dict = user_preference.director_dict
        country_dict = user_preference.country_dict
        genre_dict = user_preference.genre_dict

        actor_dict_sorted = None if actor_dict is None else OrderedDict(sorted(actor_dict.items(), reverse=True)[:10])
        director_dict_sorted = None if director_dict is None else OrderedDict(sorted(director_dict.items(), reverse=True)[:10])
        country_dict_sorted = None if country_dict is None else OrderedDict(sorted(country_dict.items(), reverse=True)[:10])
        genre_dict_sorted = None if genre_dict is None else OrderedDict(sorted(genre_dict.items(), reverse=True)[:10])

        return UserPreferenceResponse(
                id=user_preference.id,
                user_id=user_id,
                actor_dict=actor_dict_sorted,
                director_dict=director_dict_sorted,
                country_dict=country_dict_sorted,
                genre_dict=genre_dict_sorted)
