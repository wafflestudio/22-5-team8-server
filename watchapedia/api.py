from fastapi import APIRouter
from watchapedia.app.user.views import user_router
from watchapedia.app.movie.views import movie_router
from watchapedia.app.review.views import review_router
from watchapedia.app.comment.views import comment_router
from watchapedia.app.participant.views import participant_router
from watchapedia.app.collection.views import collection_router
from watchapedia.app.collection_comment.views import collection_comment_router
from watchapedia.app.search.views import search_router
from watchapedia.app.recommend.views import recommend_router
from watchapedia.app.auth.views import auth_router
from watchapedia.app.calendar.views import calendar_router
from watchapedia.app.analysis.views import analysis_router

api_router = APIRouter()

api_router.include_router(user_router, prefix='/users', tags=['users'])
api_router.include_router(movie_router, prefix='/movies', tags=['movies'])
api_router.include_router(review_router, prefix='/reviews', tags=['reviews'])
api_router.include_router(comment_router, prefix='/comments', tags=['comments'])
api_router.include_router(participant_router, prefix='/participants', tags=['participants'])
api_router.include_router(collection_router, prefix='/collections', tags=['collections'])
api_router.include_router(collection_comment_router, prefix='/collection_comments', tags=['collection_comments'])
api_router.include_router(search_router, prefix='/search', tags=['search'])
api_router.include_router(recommend_router, prefix='/recommend', tags=['recommend'])
api_router.include_router(auth_router, prefix='/auth', tags=['auth'])
api_router.include_router(calendar_router, prefix='/calendar', tags=['calendar'])
api_router.include_router(analysis_router, prefix='/analysis', tags=['analysis'])
