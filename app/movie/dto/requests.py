from pydantic import BaseModel
from common.errors import InvalidFieldFormatError
from typing import Annotated
from pydantic.functional_validators import AfterValidator

def validate_year(value: int | None) -> str | None:
    # 최초의 영화는 '열차의 도착'이란 프랑스 영화로, 1895년 작이다.
    if value is None:
        return value
    if value < 1895:
        raise InvalidFieldFormatError("year")
    
def validate_average_rating(value: float | None) -> float | None:
    if value is None:
        return value
    if value < 0.0 or value > 5.0:
        raise InvalidFieldFormatError("average_rating")

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

class AddMovieRequest(BaseModel):
    title: str
    year: Annotated[int, AfterValidator(validate_year)]
    synopsis: str | None = None
    average_rating: Annotated[float | None, AfterValidator(validate_average_rating)] = None
    running_time: Annotated[int, AfterValidator(validate_running_time)]
    grade: Annotated[str, AfterValidator(validate_grade)]