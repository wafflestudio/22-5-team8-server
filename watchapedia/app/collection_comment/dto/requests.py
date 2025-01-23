from pydantic import BaseModel
from watchapedia.common.errors import InvalidFieldFormatError
from typing import Annotated
from pydantic.functional_validators import AfterValidator

def validate_content(value: str | None) -> str | None:
    # content 필드는 500자 이하여야 함
    if value is None or len(value) > 500:
        raise InvalidFieldFormatError("content")
    return value

class CollectionCommentRequest(BaseModel):
    content: Annotated[str, AfterValidator(validate_content)]