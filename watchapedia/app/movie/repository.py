from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from typing import Annotated
from datetime import datetime
from watchapedia.app.movie.models import Movie, MovieParticipant, Chart
from watchapedia.app.participant.models import Participant

class MovieRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session
    
    # DB에 영화 추가(생성) 시엔 평점이 없으므로, 평균 평점 None으로 세팅팅
    def add_movie(
        self, 
        title: str, 
        original_title: str,
        year: int, 
        synopsis: str, 
        running_time: int, 
        grade: str | None, 
        poster_url: str | None, 
        backdrop_url: str | None
    ) -> Movie:
        movie = Movie(
            title=title,
            original_title=original_title,
            year=year,
            synopsis=synopsis,
            average_rating=None,
            running_time=running_time,
            grade=grade,
            poster_url=poster_url,
            backdrop_url=backdrop_url
        )
        self.session.add(movie)
        self.session.flush()
        return movie
    
    def update_movie(
        self, 
        movie: Movie, 
        synopsis: str | None, 
        grade: str | None, 
        average_rating: float | None, 
        poster_url: str | None, 
        backdrop_url: str | None
    ) -> None:
        if synopsis:
            movie.synopsis = synopsis
        if grade:
            movie.grade = grade
        if average_rating:
            movie.average_rating = average_rating
        if poster_url:
            movie.poster_url = poster_url
        if backdrop_url:
            movie.backdrop_url = backdrop_url
        
        self.session.flush()
    
    def update_chart(self, chart_type: str, rank: int, movie: Movie) -> None:
        chart_rank = self.get_chart_rank_by_chart_type(chart_type, movie)
        if chart_rank:
            # update chart
            chart_rank.rank = rank
            chart_rank.updated_at = datetime.now()
        else:
            # create chart
            chart_rank = Chart(
                platform=chart_type,
                rank=rank,
                updated_at=datetime.now(),
                movie=movie
            )
            self.session.add(chart_rank)
        self.session.flush()
    
    def get_chart_rank_by_chart_type(self, chart_type: str, movie: Movie) -> Chart | None:
        get_chart_query = select(Chart).filter((Chart.platform == chart_type) & (Chart.movie_id == movie.id))
        return self.session.scalar(get_chart_query)
            
    def add_movie_participant(self, movie: Movie, participant: Participant, role: str) -> None:
        movie_participant = MovieParticipant(movie.id, participant.id, role)
        self.session.add(movie_participant)
        self.session.flush()
    
    # 동명의 영화가 다수 존재. 하나로 특정하려면 다른 필드와 조합해서 검색
    def get_movie(self, title: str, year: int, running_time: int) -> Movie | None:
        get_movie_query = select(Movie).filter(
            (Movie.title==title)
            & (Movie.year==year)
            & (Movie.running_time==running_time)
        )
        return self.session.scalar(get_movie_query)

    def get_movie_by_movie_id(self, movie_id: int) -> Movie | None:
        get_movie_query = select(Movie).filter(Movie.id==movie_id)
        return self.session.scalar(get_movie_query)