from fastapi import APIRouter
from app.user.views import user_router
from app.movie.views import movie_router

api_router = APIRouter()

api_router.include_router(user_router, prefix='/users', tags=['users'])
api_router.include_router(movie_router, prefix='/movies', tags=['movies'])