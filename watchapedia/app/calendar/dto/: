from pydantic import BaseModel
from watchapedia.common.errors import InvalidFieldFormatError
from typing import Annotated
from pydantic.functional_validators import AfterValidator
from fastapi import Query, Depends
from datetime import datetime


def validate_calendar_query(calendar_q: Annotated[str, Query(..., description="YYYY-MM-DD 형식의 날짜")]) -> datetime:
    try:
        return datetime.strptime(calendar_q, "%Y-%m-%d").date()
    except ValueError:
        raise InvalidFieldFormatError("날짜 형식이 올바르지 않습니다: {date_str} (YYYY-MM-DD 형식이어야 함)")
