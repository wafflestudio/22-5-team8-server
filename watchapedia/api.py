from fastapi import APIRouter
from watchapedia.app.user.views import user_router
from watchapedia.app.auth.views import auth_router

api_router = APIRouter()

api_router.include_router(user_router, prefix='/users', tags=['users'])
api_router.include_router(auth_router, prefix='/auth', tags=['auth'])