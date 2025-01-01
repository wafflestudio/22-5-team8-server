from pydantic import BaseModel
from typing import Annotated
from pydantic.functional_validators import AfterValidator
from watchapedia.app.auth.dto.requests import validate_username, validate_password

class UserUpdateRequest(BaseModel):
    username: Annotated[str | None, AfterValidator(validate_username)] = None
    login_password: Annotated[str | None, AfterValidator(validate_password)] = None