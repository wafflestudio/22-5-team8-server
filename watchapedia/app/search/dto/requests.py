from pydantic import BaseModel
from watchapedia.common.errors import InvalidFieldFormatError
from typing import Annotated
from pydantic.functional_validators import AfterValidator

def validate_search_query(value: str | None) -> str:
    if len(value) > 100:
        raise InvalidFieldFormatError("search query")
    return value

class SearchRequest(BaseModel):
    search_query: Annotated[str | None, AfterValidator(validate_search_query)] = None
