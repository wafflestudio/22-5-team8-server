from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
from collections import defaultdict
from watchapedia.app.review.models import Review
from watchapedia.database.connection import get_db_session
from typing import Annotated
from fastapi import Depends

class CalendarRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def get_movie_id_by_date(
        self, 
        user_id: int, 
        calendar_q1: str, 
        calendar_q2: str
    ) -> dict[str, list[int]]:
        # 날짜 형식 변환 (YYYY-MM-DD → datetime)
        #start_date = datetime.strptime(calendar_q1, "%Y-%m-%d").date()
        #end_date = datetime.strptime(calendar_q2, "%Y-%m-%d").date()
        start_date = calendar_q1
        end_date = calendar_q2
        # SQLAlchemy 쿼리: 특정 user_id의 리뷰 중 created_at이 지정된 범위에 해당하는 것 조회
        query = select(
            func.date(Review.created_at).label("review_date"),
            Review.movie_id
        ).where(
            and_(
                Review.user_id == user_id,
                Review.created_at >= start_date,
                Review.created_at <= end_date
            )
        )

        # 결과 조회
        result = self.session.execute(query).all()

        # 날짜별 movie_id를 저장할 defaultdict
        movie_by_date = defaultdict(list)

        for review_date, movie_id in result:
            movie_by_date[review_date.strftime("%Y-%m-%d")].append(movie_id)

        return dict(movie_by_date)

