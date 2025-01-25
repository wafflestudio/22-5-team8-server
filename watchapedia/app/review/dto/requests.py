from pydantic import BaseModel
from watchapedia.common.errors import InvalidFieldFormatError
from typing import Annotated
from pydantic.functional_validators import AfterValidator

def validate_content(value: str | None) -> str | None:
    # content는 500자 이내여야 함
    if value is None:
        return value
    if len(value) > 500:
        raise InvalidFieldFormatError("content")
    return value

def validate_rating(value: float) -> float:
    # 별점은 0.5와 5 사이여야 함. 0은 삭제된 상태를 의미
    if value is None:
        return value
    if value > 5 or value < 0:
        raise InvalidFieldFormatError("rating")
    return value

def validate_status(value: str | None) -> str | None:
    # status는 None이거나 "WatchList"거나 "Watching"이어야 함
    if value is None:
        return value
    if value not in ["WatchList", "Watching", ""] :
        raise InvalidFieldFormatError("status")
    return value

class ReviewCreateRequest(BaseModel):
    content: Annotated[str | None, AfterValidator(validate_content)] = None
    rating: Annotated[float | None, AfterValidator(validate_rating)] = None
    spoiler: bool
    status: Annotated[str | None, AfterValidator(validate_status)] = None

class ReviewUpdateRequest(BaseModel):
    content: Annotated[str | None, AfterValidator(validate_content)] = None
    rating: Annotated[float | None, AfterValidator(validate_rating)] = None
    spoiler: bool | None
    status: Annotated[str | None, AfterValidator(validate_status)] = None
