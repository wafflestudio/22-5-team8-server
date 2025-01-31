from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
from collections import defaultdict
from watchapedia.app.review.models import Review
from watchapedia.database.connection import get_db_session
from typing import Annotated
from fastapi import Depends
from datetime import date, datetime

class CalendarRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def get_movie_id_by_date(
        self, 
        user_id: int, 
        calendar_q1: date, 
        calendar_q2: date
    ) -> dict[str, list[int]]:
        
        start_date = calendar_q1.strftime("%Y-%m-%d")
        end_date = calendar_q2.strftime("%Y-%m-%d")

        query = select(
            Review.view_date,  
            Review.movie_id
        ).where(
            Review.user_id == user_id
        )

        result = self.session.execute(query).all()

        movie_by_date = defaultdict(list)
    
        for row in result:
            view_date_dict, movie_id = row  
        
            if isinstance(view_date_dict, dict):  
                for date_str in view_date_dict.keys():  
                    if start_date <= date_str <= end_date:  
                        movie_by_date[date_str].append(movie_id)

        return dict(movie_by_date)
