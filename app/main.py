from fastapi import FastAPI
from app.api import api_router
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.requests import Request
from common.errors import MissingRequiredFieldError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.include_router(api_router, prefix="/api")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key='secret-string')

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for error in exc.errors():
        if isinstance(error, dict) and error.get("type", None) == "missing":
            raise MissingRequiredFieldError()
    return await request_validation_exception_handler(request, exc)