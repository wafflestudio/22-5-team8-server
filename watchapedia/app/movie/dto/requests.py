from pydantic import BaseModel
from watchapedia.common.errors import InvalidFieldFormatError
from typing import Annotated
from pydantic.functional_validators import AfterValidator
import re

URL_PATTERN = re.compile(r"(https?://)?(www.)?[-a-zA-Z0-9@:%.+~#=]{2,256}.[a-z]{2,6}\b([-a-zA-Z0-9@:%+.~#?&//=]*)")

def validate_year(value: int | None) -> str:
    # 최초의 영화는 '열차의 도착'이란 프랑스 영화로, 1895년 작이다.
    if value is None or value < 1895:
        raise InvalidFieldFormatError("year")
    return value

def validate_running_time(value: int | None) -> int:
    if value is None or value < 1 or value > 900:
        raise InvalidFieldFormatError("running time")
    return value
    
def validate_grade(value: str | None) -> str:
    allowed_grades = {"전체", "12세", "15세", "청불"}
    if value is None or value not in allowed_grades:
        raise InvalidFieldFormatError("grade")
    return value

def validate_url(value: str | None) -> str:
    if value is None:
        return value
    if not re.match(URL_PATTERN, value):
        raise InvalidFieldFormatError("url")
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
    poster_url: Annotated[str | None, AfterValidator(validate_url)] = None
    backdrop_url: Annotated[str | None, AfterValidator(validate_url)] = None
    genres: list[str]
    countries: list[str]
    participants: list[AddParticipantsRequest]
    
class UpdateMovieRequest(BaseModel):
    synopsis: str | None = None
    grade: Annotated[str | None, AfterValidator(validate_grade)] = None
    average_rating: float | None = None
    poster_url: Annotated[str | None, AfterValidator(validate_url)] = None
    backdrop_url: Annotated[str | None, AfterValidator(validate_url)] = None