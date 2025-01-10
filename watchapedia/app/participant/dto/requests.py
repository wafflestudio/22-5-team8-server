from typing import Annotated
from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator
from watchapedia.app.movie.dto.requests import validate_url
from watchapedia.app.review.dto.requests import validate_content

class ParticipantProfileUpdateRequest(BaseModel):
    name: str | None = None
    profile_url: Annotated[str | None, AfterValidator(validate_url)] = None
    biography: Annotated[str | None, AfterValidator(validate_content)] = None