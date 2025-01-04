from pydantic import BaseModel
from watchapedia.common.errors import InvalidFieldFormatError
from typing import Annotated
from pydantic.functional_validators import AfterValidator

def validate_year(value: int | None) -> str | None:
    # 최초의 영화는 '열차의 도착'이란 프랑스 영화로, 1895년 작이다.
    if value is None:
        return value
    if value < 1895:
        raise InvalidFieldFormatError("year")

def validate_running_time(value: int | None) -> int | None:
    if value is None:
        return value
    if value < 1 or value > 900:
        raise InvalidFieldFormatError("running time")
    
def validate_grade(value: str | None) -> str | None:
    if value is None:
        return value
    allowed_grades = {"전체", "12세", "15세", "청불"}
    if value not in allowed_grades:
        raise InvalidFieldFormatError("grade")

def validate_url(value: str | None) -> str | None:
    if value is None:
        return value
    

class AddParticipantsRequest(BaseModel):
    name: str
    role: str
    profile_url: str | None = None

class AddMovieRequest(BaseModel):
    title: str
    original_title: str
    year: Annotated[int, AfterValidator(validate_year)]
    synopsis: str | None = None
    running_time: Annotated[int, AfterValidator(validate_running_time)]
    grade: Annotated[str | None, AfterValidator(validate_grade)] = None
    poster_url: str | None = None
    backdrop_url: str | None = None
    genres: list[str]
    countries: list[str]
    participants: list[AddParticipantsRequest]
    
class UpdateMovieRequest(BaseModel):
    synopsis: str | None = None
    grade: Annotated[str | None, AfterValidator(validate_grade)] = None
    poster_url: str | None = None
    backdrop_url: str | None = None