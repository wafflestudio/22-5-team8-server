from pydantic import BaseModel
from watchapedia.common.errors import InvalidFieldFormatError
from typing import Annotated
from pydantic.functional_validators import AfterValidator
from fastapi import Query

def validate_search_query(search_q: str = Query(...)) -> str:
    if len(search_q) > 100:
        raise InvalidFieldFormatError("search query")
    return search_q
