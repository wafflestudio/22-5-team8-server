from sqlalchemy.orm import Session
from sqlalchemy import func, select, cast, Float
from fastapi import Depends

from watchapedia.database.connection import get_db_session
from typing import Annotated
from watchapedia.app.analysis.models import UserRating, UserPreference
from watchapedia.app.review.models import Review
from watchapedia.app.movie.models import Movie,MovieParticipant
from watchapedia.app.participant.models import Participant
from watchapedia.app.genre.models import Genre, MovieGenre
from watchapedia.app.country.models import Country, MovieCountry
import math
import sys


class UserPreferenceRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def update_preference(
            self,
            user_preference: UserPreference,
            actor_dict: dict[int, tuple[float, int]],
            director_dict: dict[int, tuple[float, int]],
            country_dict: dict[int, tuple[float, int]],
            genre_dict: dict[int, tuple[float, int]]
            ) -> UserPreference:
        user_preference.actor_dict = actor_dict
        user_preference.director_dict = director_dict
        user_preference.country_dict = country_dict
        user_preference.genre_dict = genre_dict

        self.session.flush()

        return user_preference

    def get_user_preference_by_user_id(
            self,
            user_id: int
            ) -> UserPreference:
        get_preference_query = select(UserPreference).where(UserPreference.user_id == user_id)
        return self.session.scalar(get_preference_query)


    def update_user_preference_actor(
        self,
        user_id: int,
        movie_id: int,
        user_rating: UserRating,
        review_list: list[Review]
        ) -> tuple[dict, dict, dict, dict]:
        # 0. 전체 평가한 영화 수 계산(공통값)
        rating_avg_tot = user_rating.rating_avg
        rating_num_tot = user_rating.rating_num

        # 1. actor_list : 영화에 출연한 배우들 id
            # review/service 함수로 review_id로 review 얻고(service에서) 이를 통해 movie_id 얻기
        actor_list = [
                actor_id for (actor_id,) in 
                self.session.query(Participant.id)
                .join(MovieParticipant)
                .filter(MovieParticipant.movie_id == movie_id)
                .filter(MovieParticipant.role == "배우")
                .all()] #OK

        director_list = [
                director_id for (director_id,) in
                self.session.query(Participant.id)
                .join(MovieParticipant)
                .filter(MovieParticipant.movie_id == movie_id)
                .filter(MovieParticipant.role == "감독")
                .all()]

        genre_list = [
                genre_id for (genre_id,) in
                self.session.query(Genre.id)
                .join(MovieGenre)
                .filter(MovieGenre.movie_id == movie_id)
                .all()] 

        country_list = [
                country_id for (country_id,) in
                self.session.query(Country.id)
                .join(MovieCountry)
                .filter(MovieCountry.movie_id == movie_id)
                .all()] 

        # 2. 배우들 하나씩 rating_avg_act / 평가한 배우 영화 수 계산
        rating_act_dict = dict() #{actor_id: (movie_count, rating_avg) 
        rating_dir_dict = dict()
        rating_gen_dict = dict()
        rating_coun_dict = dict()

        review_movie_ids = [review.movie_id for review in review_list] # 리뷰한 영화 id 목록 OK

        for participant_id in actor_list: # 배우별
            # 배우로서 출연한 영화목록
            result = (
                self.session.query(
                    func.count(func.distinct(MovieParticipant.movie_id)),  # 출연한 영화 개수
                    func.avg(Review.rating)  # 평균 평점
                )
                .join(MovieParticipant, Review.movie_id == MovieParticipant.movie_id)
                .filter(MovieParticipant.participant_id == participant_id)
                .filter(MovieParticipant.role.like("%배우%"))
                .filter(MovieParticipant.movie_id.in_(review_movie_ids))  # 리뷰에 있는 영화만 선택
                .one()  # 단일 결과 반환
            )
            movie_count_actor = result[0]
            rating_actor = result[1]
            rating_act_dict[participant_id] = (movie_count_actor, rating_actor)

        for participant_id in director_list:
            result = (
                self.session.query(
                    func.count(func.distinct(MovieParticipant.movie_id)),
                    func.avg(Review.rating)
                )
                .join(MovieParticipant, Review.movie_id == MovieParticipant.movie_id)
                .filter(MovieParticipant.participant_id == participant_id)
                .filter(MovieParticipant.role.like("%감독%"))
                .filter(MovieParticipant.movie_id.in_(review_movie_ids))
                .one()
            )
            movie_count_director = result[0]
            rating_director = result[1]
            rating_dir_dict[participant_id] = (movie_count_director, rating_director)

        for genre_id in genre_list: 
            result = (
                self.session.query(
                    func.count(func.distinct(MovieGenre.movie_id)),
                    func.avg(Review.rating) 
                )
                .join(MovieGenre, Review.movie_id == MovieGenre.movie_id)
                .filter(MovieGenre.genre_id == genre_id)
                .filter(MovieGenre.movie_id.in_(review_movie_ids))
                .one()  
            )
            movie_count_genre = result[0]
            rating_genre = result[1]
            rating_gen_dict[genre_id] = (movie_count_genre, rating_genre)

        for country_id in country_list:
            result = (
                self.session.query(
                    func.count(func.distinct(MovieCountry.movie_id)),
                    func.avg(Review.rating)
                )
                .join(MovieCountry, Review.movie_id == MovieCountry.movie_id)
                .filter(MovieCountry.country_id == country_id)
                .filter(MovieCountry.movie_id.in_(review_movie_ids))
                .one()
            )
            movie_count_country = result[0]
            rating_country = result[1]
            rating_coun_dict[country_id] = (movie_count_country, rating_country)


        # 3. 배우 별 점수 계산 -> 점수 top 10 배우들과 중복없이 set으로 합친후 정렬 -> 상위 10개만 잘라 반환.
        actor_dict_pre = self.get_user_preference_by_user_id(user_id).actor_dict
        director_dict_pre = self.get_user_preference_by_user_id(user_id).director_dict
        genre_dict_pre = self.get_user_preference_by_user_id(user_id).genre_dict
        country_dict_pre = self.get_user_preference_by_user_id(user_id).country_dict

            # 공식 일단은 간단히
        if rating_act_dict == None:
            actor_dict_cur = None
        else:
            actor_dict_cur = dict()
            for pid, (movie_count_actor, rating_actor) in rating_act_dict.items():
                if movie_count_actor == 0:
                    pass
                else:
                    if rating_actor == None:
                        # 해당 영화 리뷰는 있지만, 평점이 없는 경우.
                        actor_dict_cur[pid] = (50+50*(movie_count_actor/(movie_count_actor+10)), movie_count_actor)
                    else:
                        actor_dict_cur[pid] = (max(0, min(100,50+(rating_actor-rating_avg_tot)*100*(movie_count_actor/math.log(rating_num_tot+2))**0.5+50*(movie_count_actor/(movie_count_actor+10)))), movie_count_actor)       
            #actor_dict_cur = {pid: (max(0, min(100,50+(rating_actor-rating_avg_tot)*100*(movie_count_actor/math.log(rating_num_tot+2))**0.5+50*(movie_count_actor/(movie_count_actor+10)))), movie_count_actor) for pid, (movie_count_actor, rating_actor) in rating_act_dict.items()}
        if rating_dir_dict == None:
            director_dict_cur = None
        else:
            director_dict_cur = dict()
            for pid, (movie_count_director, rating_director) in rating_dir_dict.items():
                if movie_count_director == 0:
                    pass
                else:
                    if rating_director == None:
                        director_dict_cur[pid] = (50+50*(movie_count_director/(movie_count_director+10)), movie_count_director)
                    else:
                        director_dict_cur[pid] = (max(0, min(100,50+(rating_director-rating_avg_tot)*100*(movie_count_director/math.log(rating_num_tot+2))**0.5+50*(movie_count_director/(movie_count_director+10)))), movie_count_director)
            #director_dict_cur = {pid: (max(0, min(100,50+(rating_director-rating_avg_tot)*100*(movie_count_director/math.log(rating_num_tot+2))**0.5+50*(movie_count_director/(movie_count_director+10)))), movie_count_director) for pid, (movie_count_director, rating_director) in rating_dir_dict.items()}
        if rating_gen_dict == None:
            genre_dict_cur = None
        else:
            genre_dict_cur = dict()
            for pid, (movie_count_genre, rating_genre) in rating_gen_dict.items():
                if movie_count_genre == 0:
                    pass
                else:
                    if rating_genre == None:
                        genre_dict_cur[pid] = (50+50*(movie_count_genre/(movie_count_genre+10)), movie_count_genre)
                    else:
                        genre_dict_cur[pid] = (max(0, min(100,50+(rating_genre-rating_avg_tot)*100*(movie_count_genre/math.log(rating_num_tot+2))**0.5+50*(movie_count_genre/(movie_count_genre+10)))), movie_count_genre)
            #genre_dict_cur = {pid: (max(0, min(100,50+(rating_genre-rating_avg_tot)*100*(movie_count_genre/math.log(rating_num_tot+2))**0.5+50*(movie_count_genre/(movie_count_genre+10)))), movie_count_genre) for pid, (movie_count_genre, rating_genre) in rating_gen_dict.items()}
        if rating_coun_dict == None:
            country_dict_cur = None
        else:
            country_dict_cur = dict()
            for pid, (movie_count_country, rating_country) in rating_coun_dict.items():
                if movie_count_country == 0:
                    pass
                else:
                    if rating_country == None:
                        country_dict_cur[pid] = (50+50*(movie_count_country/(movie_count_country+10)), movie_count_country)
                    else:
                        country_dict_cur[pid] = (max(0, min(100,50+(rating_country-rating_avg_tot)*100*(movie_count_country/math.log(rating_num_tot+2))**0.5+50*(movie_count_country/(movie_count_country+10)))), movie_count_country)
            #country_dict_cur = {pid: (max(0, min(100,50+(rating_country-rating_avg_tot)*100*(movie_count_country/math.log(rating_num_tot+2))**0.5+50*(movie_count_country/(movie_count_country+10)))), movie_count_country) for pid, (movie_count_country, rating_country) in rating_coun_dict.items()}

        if actor_dict_pre:
            actor_dict_pre = {int(k): v for k, v in actor_dict_pre.items()} #json 직렬화에 의한 key str 변환 보정.
            if len(actor_dict_cur) == 0:
                merged_actor_dict = actor_dict_pre
            else:
                merged_actor_dict = {**actor_dict_pre, **actor_dict_cur}  # actor_dict_cur이 우선 적용됨
        else: # 처음 추가하는거라 none인 상태
            merged_actor_dict = actor_dict_cur
        if director_dict_pre:
            director_dict_pre = {int(k): v for k, v in director_dict_pre.items()}
            if len(director_dict_cur) == 0:
                merged_director_dict = director_dict_pre
            else:
                merged_director_dict = {**director_dict_pre, **director_dict_cur}
        else:
            merged_director_dict = director_dict_cur
        if genre_dict_pre:
            genre_dict_pre = {int(k): v for k, v in genre_dict_pre.items()}
            if len(genre_dict_cur) == 0:
                merged_genre_dict = genre_dict_pre
            else:
                merged_genre_dict = {**genre_dict_pre, **genre_dict_cur}
        else:
            merged_genre_dict = genre_dict_cur
        if country_dict_pre:
            country_dict_pre = {int(k): v for k, v in country_dict_pre.items()}
            if len(country_dict_cur) == 0:
                merged_country_dict = country_dict_pre
            else:
                merged_country_dict = {**country_dict_pre, **country_dict_cur}
        else:
            merged_country_dict = country_dict_cur

        print('merged_actor_dict', merged_actor_dict)
        if merged_actor_dict == None:
            actor_dict_update = None
        else:
            actor_dict_update = dict(sorted(merged_actor_dict.items(), key=lambda item: item[1][0], reverse=True))
        if merged_director_dict == None:
            director_dict_update = None
        else:
            director_dict_update = dict(sorted(merged_director_dict.items(), key=lambda item: item[1][0], reverse=True))
        if merged_genre_dict == None:
            genre_dict_update = None
        else:
            genre_dict_update = dict(sorted(merged_genre_dict.items(), key=lambda item: item[1][0], reverse=True))
        if merged_country_dict == None:
            country_dict_update = None
        else:
            country_dict_update = dict(sorted(merged_country_dict.items(), key=lambda item: item[1][0], reverse=True))
        print('actor_dict_update', actor_dict_update)

        return (actor_dict_update, director_dict_update, genre_dict_update, country_dict_update)

class UserRatingRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def create_rating(
            self,
            user_id: int
            ) -> None:
        user_rating = UserRating(
                user_id=user_id,
                rating_num=0,
                rating_avg=None,
                rating_dist=None,
                rating_mode=None,
                rating_message=None,
                viewing_time=None,
                viewing_message=None
                )

        self.session.add(UserRating)

    def update_rating(
            self, 
            user_rating: UserRating, 
            rating_num: int, 
            rating_avg: float, 
            rating_dist: dict[float, int], 
            rating_mode: float,
            rating_message: str,
            viewing_time: int,
            viewing_message: str
            ) -> UserRating:
        user_rating.rating_num = rating_num
        user_rating.rating_avg = rating_avg
        user_rating.rating_dist = rating_dist
        user_rating.rating_mode = rating_mode
        user_rating.rating_message = rating_message
        user_rating.viewing_time = viewing_time
        user_rating.viewing_message = viewing_message

        self.session.flush()

        return user_rating

    def get_user_rating_by_user_id(
            self,
            user_id: int
            ) -> UserRating:
        get_rating_query = select(UserRating).where(UserRating.user_id == user_id)
        return self.session.scalar(get_rating_query)

    def get_user_viewing_time(
            self,
            user_id: int
            ) -> int:

        total_running_time = (
            self.session.query(func.sum(Movie.running_time))
            .join(Review, Review.movie_id == Movie.id)  # Review에서 Movie로 조인
            .filter(Review.user_id == user_id)  # 특정 유저가 작성한 리뷰만 선택
            .scalar()  # 단일 값 반환
        )

        print(total_running_time)

        if total_running_time == None:
            return 0
        else:
            total_running_hour = total_running_time // 60
            return total_running_hour


    def get_user_rating_metrices(
            self,
            user_id: int
            ) -> dict:

        query = self.session.query(
            func.count(Review.id).label("count"),
            func.avg(Review.rating).cast(Float).label("average")
        ).filter(Review.user_id == user_id, Review.rating.isnot(None))

        result = query.first()


        return {
                "rating_num": result.count,
                "rating_avg": result.average
                }

    def get_user_rating_dist(
            self,
            user_id: int
            ) -> dict:
        distribution = (
                self.session.query(Review.rating, func.count(Review.rating).label("count"))
                .filter(Review.user_id == user_id, Review.rating.isnot(None))
                .group_by(Review.rating)
                .order_by(Review.rating.asc())
                .all()
                )

        rating_counts = {round(i/2, 1): 0 for i in range(1, 11)}
        for row in distribution:
            rating_counts[row.rating] = row.count
        return rating_counts
