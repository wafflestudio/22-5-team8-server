from pydantic import BaseModel
from common.errors import InvalidFieldFormatError
import re
from typing import Annotated
from pydantic.functional_validators import AfterValidator

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
LOGIN_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_.]{6,20}$")

def validate_username(value: str | None) -> str | None:
    # username 필드는 3자 이상 20자 이하의 영문자, 숫자, 언더스코어(_), 하이픈(-)만 허용
    if value is None:
        return value
    if not re.match(USERNAME_PATTERN, value):
        raise InvalidFieldFormatError("username")
    return value

def validate_login_id(value: str | None) -> str | None:
    # login_id 필드는 6자 이상 20자 이하의 영문자, 숫자, 언더스코어(_), 닷(.)만 하용
    if value is None:
        return value
    if not re.match(LOGIN_ID_PATTERN, value):
        raise InvalidFieldFormatError("login_id")
    return value

def validate_password(value: str | None) -> str | None:
    # login_password 필드는 8자 이상 20자 이하의 영문자, 숫자, 특수문자 중 2가지 이상을 포함해야 함
    if value is None:
        return value
    if len(value) < 8 or len(value) > 20:
        raise InvalidFieldFormatError("login_password")

    contains_uppercase = False
    contains_lowercase = False
    contains_digit = False
    contains_special = False

    for char in value:
        if char.isupper():
            contains_uppercase = True
        elif char.islower():
            contains_lowercase = True
        elif char.isdigit():
            contains_digit = True
        else:
            contains_special = True

    constraints_cardinality = sum(
        [contains_uppercase, contains_lowercase, contains_digit, contains_special]
    )
    if constraints_cardinality < 2:
        raise InvalidFieldFormatError()

    return value

class UserSignupRequest(BaseModel):
    username: Annotated[str, AfterValidator(validate_username)]
    login_id: Annotated[str, AfterValidator(validate_login_id)]
    login_password: Annotated[str, AfterValidator(validate_password)]

class UserSigninRequest(BaseModel):
    login_id: Annotated[str, AfterValidator(validate_login_id)]
    login_password: Annotated[str, AfterValidator(validate_password)]