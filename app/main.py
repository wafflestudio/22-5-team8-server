from fastapi import FastAPI
from app.api import api_router
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.requests import Request
from common.errors import MissingRequiredFieldError

app = FastAPI()

app.include_router(api_router, prefix="/api")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for error in exc.errors():
        if isinstance(error, dict) and error.get("type", None) == "missing":
            raise MissingRequiredFieldError()
    return await request_validation_exception_handler(request, exc)