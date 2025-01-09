from fastapi import APIRouter
from watchapedia.app.user.views import user_router
from watchapedia.app.movie.views import movie_router
from watchapedia.app.review.views import review_router
from watchapedia.app.comment.views import comment_router

api_router = APIRouter()

api_router.include_router(user_router, prefix='/users', tags=['users'])
api_router.include_router(movie_router, prefix='/movies', tags=['movies'])
api_router.include_router(review_router, prefix='/reviews', tags=['reviews'])
api_router.include_router(comment_router, prefix='/comments', tags=['comments'])