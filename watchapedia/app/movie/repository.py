from sqlalchemy import Sequence, func, select
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends
from watchapedia.app.country.models import Country
from watchapedia.app.genre.models import Genre
from watchapedia.database.connection import get_db_session
from typing import Annotated
from datetime import datetime
from watchapedia.app.movie.models import Movie, MovieParticipant, Chart
from watchapedia.app.review.models import Review
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
        
    def search_movie_list(
        self,
        title: str | None = None,
        chart_type: str | None = None,
        min_rating: float | None = None,
        max_rating: float | None = None,
        genres: list[str] | None = None,
        countries: list[str] | None = None,
        participant_id: int | None = None
    ) -> Sequence[Movie]:
        type_dict = {"box_office": 30, "watcha_buying": 30, "watcha10": 10, "netflix": 10}
        stmt = select(Movie).options(
            joinedload(Movie.genres),
            joinedload(Movie.countries),
            joinedload(Movie.movie_participants).joinedload(MovieParticipant.participant)
        )   # eager loading

        if title:
            stmt = stmt.where(Movie.title.ilike(f"%{title}%"))  # 대소문자 구분X, 부분 일치 지원

        if chart_type:
            stmt = stmt.join(Chart).where(Chart.platform == chart_type)

        if min_rating:
            stmt = stmt.where(Movie.average_rating >= min_rating)
        if max_rating:
            stmt = stmt.where(Movie.average_rating <= max_rating)

        if genres:
            stmt = stmt.join(Movie.genres).filter(Genre.name.in_(genres))  # 해당 장르 중 하나라도 포함된 영화만 찾음
            stmt = stmt.group_by(Movie.id).having(func.count(Genre.id) == len(genres))
        
        if countries:
            stmt = stmt.join(Movie.countries).filter(Country.name.in_(countries))  # 해당 장르 중 하나라도 포함된 영화만 찾음
            stmt = stmt.group_by(Movie.id).having(func.count(Country.id) == len(countries))

        if participant_id:
            stmt = stmt.join(Movie.movie_participants).where(MovieParticipant.participant_id == participant_id)

        
        # 최신 순으로 정렬 - 역순으로
        if chart_type:
            stmt = stmt.order_by(Chart.updated_at.desc(), Chart.rank.desc())
    
        # 반환 개수 제한
        limit = type_dict.get(chart_type, None)
        if limit:
            stmt = stmt.limit(limit)
            
        # 중복 제거
        stmt = stmt.distinct()

        movies = self.session.scalars(stmt).unique()
        return movies
    
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

    def update_average_rating(self, movie: Movie) -> None:
        reviews = movie.reviews
        total_rating = 0.0
        for review in reviews :
            total_rating += review.rating
        movie.average_rating = round(total_rating / len(reviews), 1)
        self.session.flush()