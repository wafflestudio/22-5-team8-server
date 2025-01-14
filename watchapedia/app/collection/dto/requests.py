from pydantic import BaseModel
from watchapedia.common.errors import InvalidFieldFormatError
from typing import Annotated
from pydantic.functional_validators import AfterValidator

def validate_title(value: str | None) -> str | None:
    # title는 100자 이내여야 함
    if value is None:
        return value
    if len(value) > 100:
        raise InvalidFieldFormatError("title")
    return value

def validate_overview(value: str | None) -> str | None:
    # overview는 500자 이내여야 함
    if value is None:
        return value
    if len(value) > 500:
        raise InvalidFieldFormatError("overview")
    return value


class CollectionCreateRequest(BaseModel):
    title: Annotated[str, AfterValidator(validate_title)]
    overview: Annotated[str | None, AfterValidator(validate_overview)] = None
    movie_ids: list[int] | None = None

class CollectionUpdateRequest(BaseModel):
    title: Annotated[str | None, AfterValidator(validate_title)] = None
    overview: Annotated[str | None, AfterValidator(validate_overview)] = None
    movie_ids: list[int] | None = None
