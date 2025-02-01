from typing import Annotated
from fastapi import Depends
from watchapedia.app.analysis.models import UserRating, UserPreference
from watchapedia.app.analysis.repository import UserRatingRepository
from watchapedia.app.analysis.dto.responses import UserRatingResponse
from watchapedia.app.analysis.repository import UserPreferenceRepository
from watchapedia.app.review.repository import ReviewRepository

from collections import OrderedDict  
from watchapedia.app.user.repository import UserRepository 
from watchapedia.app.participant.repository import ParticipantRepository 
from watchapedia.app.genre.repository import GenreRepository 
from watchapedia.app.country.repository import CountryRepository 

class UserPreferenceService():
    def __init__(self,
            user_preference_repository: Annotated[UserPreferenceRepository, Depends()],
            review_repository: Annotated[ReviewRepository, Depends()],
            user_rating_repository: Annotated[UserRatingRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()],
            participant_repository: Annotated[ParticipantRepository, Depends()],
            country_repository: Annotated[CountryRepository, Depends()],
            genre_repository: Annotated[GenreRepository, Depends()]     
            ) -> None:
        self.user_preference_repository = user_preference_repository
        self.review_repository = review_repository
        self.user_rating_repository = user_rating_repository
        self.user_repository = user_repository
        self.participant_repository = participant_repository
        self.country_repository = country_repository
        self.genre_repository = genre_repository

    def get_transform_dict(self,
            actor_dict: OrderedDict,
            director_dict: OrderedDict,
            genre_dict: OrderedDict,
            country_dict: OrderedDict
            ) -> tuple[OrderedDict]:

        actor_dict_transform = OrderedDict()
        director_dict_transform = OrderedDict()
        genre_dict_transform = OrderedDict()
        country_dict_transform = OrderedDict()
        if actor_dict == None or len(actor_dict) == 0:
            actor_dict_transform = None
        else:
            for actor_id, value in actor_dict.items():
                actor = self.participant_repository.get_participant_by_id(actor_id)
                actor_dict_transform[actor.name] = value
        if director_dict == None or len(director_dict)==0:

            director_dict_transform = None
        else:
            for director_id, value in director_dict.items():
                director = self.participant_repository.get_participant_by_id(director_id)
                director_dict_transform[director.name] = value

        if genre_dict == None or len(genre_dict)==0:
            genre_dict_transform = None
        else:
            for genre_id, value in genre_dict.items():
                genre = self.genre_repository.get_genre_by_id(genre_id)
                genre_dict_transform[genre.name] = value

        if country_dict == None or len(country_dict)==0:
            country_dict_transform = None
        else:
            for country_id, value in country_dict.items():
                country = self.country_repository.get_country_by_id(country_id)
                country_dict_transform[country.name] =value
        return (actor_dict_transform, director_dict_transform, genre_dict_transform, country_dict_transform)
    
    def update_preference(self,
            user_id,
            review_id,
            delete=False,
            movie_id=None) -> None:
        if delete == False: # review create, update
            recent_review = self.review_repository.get_review_by_review_id(review_id) #OK
            movie_id = recent_review.movie_id #OK
        review_list = self.review_repository.get_reviews_by_user_id(user_id)
        user_rating = self.user_rating_repository.get_user_rating_by_user_id(user_id)


        user_preference = self.user_preference_repository.get_user_preference_by_user_id(user_id)
        actor_dict, director_dict, country_dict, genre_dict = self.user_preference_repository.update_user_preference_actor(user_id, movie_id, user_rating, review_list)
        self.user_preference_repository.update_preference(user_preference, actor_dict, director_dict, country_dict, genre_dict) # UserPreferece 반환(우선은 None처리)
        #self.user_preference_repository.update_preference(user_preference, test)

    def get_user_preference_by_user_id(self,
            user_id
            ) -> UserPreference:
        return self.user_preference_repository.get_user_preference_by_user_id(user_id)

class UserRatingService():
    def __init__(self,
            user_rating_repository: Annotated[UserRatingRepository, Depends()]
            ) -> None:
        self.user_rating_repository = user_rating_repository

    def create_rating(
            self,
            user_id: int
            ) -> None:
        self.user_rating_repository.create_rating(user_id)

    def update_rating(
            self,
            user_id: int
            ) -> None:
        user_rating = self.user_rating_repository.get_user_rating_by_user_id(user_id)
        # user_rating - user 연결 logic 어딘가에 구현 필요
        # 혹은 get_user_by_user_id 이용해서 구현해야 함.
        user_rating_metrices = self.user_rating_repository.get_user_rating_metrices(user_id)
        user_rating_dist = self.user_rating_repository.get_user_rating_dist(user_id)
        user_viewing_time = self.user_rating_repository.get_user_viewing_time(user_id)

        rating_num = user_rating_metrices["rating_num"]
        rating_avg = user_rating_metrices["rating_avg"]
        rating_message = self.get_user_rating_message(rating_avg)
        rating_dist_dict = user_rating_dist
        viewing_message = self.get_user_viewing_message(user_viewing_time)

        if rating_dist_dict:
            rating_mode = max(rating_dist_dict, key=rating_dist_dict.get)
        else:
            rating_mode = None

        update_rating = self.user_rating_repository.update_rating(user_rating, rating_num, rating_avg, rating_dist_dict, rating_mode, rating_message, user_viewing_time, viewing_message)

        return self._process_user_rating_response(user_id=user_id, user_rating=update_rating)

    def get_user_rating_by_user_id(
            self,
            user_id: int
            ) -> UserRating:
        return self.user_rating_repository.get_user_rating_by_user_id(user_id)

    def get_user_rating_message(
            self,
            rating_avg: int
            ) -> str | None:
        if rating_avg == None:
            return None
        elif rating_avg >=4.6:
            return "5점 뿌리는 '부처님 급' 아량의 소유자"
        elif rating_avg >=4.4:
            return "영화면 마냥 다 좋은 '천사 급' 착한 사람♥"
        elif rating_avg >=4.3:
            return "남 작품에 욕 잘 못하는 착한 품성의 '돌고래 파'"
        elif rating_avg >=4.1:
            return "별점에 다소 관대한 경향이 있는 '다 주고파'"
        elif rating_avg >=4.0:
            return "남들보다 별점을 조금 후하게 주는 '인심파'"
        elif rating_avg >=3.9:
            return "영화를 정말로 즐길 줄 아는 '현명파'"
        elif rating_avg >=3.8:
            return "편식 없이 골고루 보는 '균형파'"
        elif rating_avg >=3.6:
            return "대중의 평가에 잘 휘둘리지 않는 '지조파'"
        elif rating_avg >=3.5:
            return "평가에 있어 주관이 뚜렷한 '소나무파'"
        elif rating_avg >=3.4:
            return "대체로 영화를 즐기지만 때론 혹평도 마다치 않는 '이성파'"
        elif rating_avg >=3.2:
            return "평가에 상대적으로 깐깐한 '깐새우파'"
        elif rating_avg >=3.0:
            return "작품을 남들보다 진지하고 비판적으로 보는 '지성파'"
        elif rating_avg >=2.8:
            return "작품을 대단히 냉정하게 평가하는 '냉장고파'"
        elif rating_avg >=2.5:
            return "웬만해서는 호평을 하지 않는 매서운 '독수리파'"
        elif rating_avg >=2.0:
            return "별점을 대단히 짜게 주는 한줌의 '소금' 같은 분 :)"
        elif rating_avg >=1.2:
            return "웬만해선 영화에 만족하지 않는 '헝그리파'"
        elif rating_avg >=0.5:
            return "세상 영화들에 불만이 많으신 '개혁파'"
        else:
            return None

    def get_user_viewing_message(
            self,
            viewing_time: int
            ) -> str | None:

        if viewing_time < 100:
            return "평가하는거 나름 되게 재밌는데 어서 더 평가를..."
        elif viewing_time < 200:
            return "영화 본 시간으로 아직 평균에 못 미쳐요ㅠ"
        elif viewing_time < 300:
            return "상위 30%만큼 영화를 보셨어요. 그래도 상위권!"
        elif viewing_time < 400:
            return "이제 자기만의 영화보는 관점이 생기셨을 거예요."
        elif viewing_time < 500:
            return "이제 자기만의 영화보는 관점이 생기셨을 거예요."
        elif viewing_time < 600:
            return "인생의 3주는 순수하게 영화 본 시간. 대단합니다."
        elif viewing_time < 750:
            return "일주일에 두 편씩 1년이면 상위 5% 매니아예요."
        elif viewing_time < 800:
            return "단언컨대 이 정도면 어디 가서 영화로 꿀리진 않을겁니다."
        elif viewing_time < 950:
            return "상위 5% 진입! 공식적인 영화인입니다."
        elif viewing_time < 1100:
            return "대..대단합니다. 순수 영화 본 시간 1000시간 돌파!"
        elif viewing_time < 1200:
            return "영화 본 시간으로 상위 3%! 왓챠가 보증하는 영화 내공인!"
        elif viewing_time < 1350:
            return "살면서 순수하게 영화 본 시간 50일 돌파! 상상이 되세요?"
        elif viewing_time < 1500:
            return "이 정도면 영화에서 인생을 통째로 배웠을 수준."
        elif viewing_time < 1600:
            return "영화를 공부하는 영화학도가 보통 이 정도 본답니다."
        elif viewing_time < 1700:
            return "상위 0.1%의 고지가 저 앞에 보여요."
        elif viewing_time < 1950:
            return "상위 0.1%의 왓챠 보증 '1등급 영화 내공인'"
        elif viewing_time < 2400:
            return "영화 1000작을 넘게 본 영화 '아마추어 영화인'"
        elif viewing_time < 2700:
            return "100일 동안 영화 본 '웅녀급 영화인'"
        elif viewing_time < 3000:
            return "영화 감독을 꿈꿀지 모를 '영화 프로페셔널'"
        elif viewing_time < 3500:
            return "3000시간을 영화 본 '상위 0.03%의 매니아'"
        elif viewing_time < 4000:
            return "상위 0.01%에 꼽히는 '베테랑 사회인'"
        elif viewing_time < 5000:
            return "국내에 몇 안되는 '영화 Expert'"
        elif viewing_time < 6529:
            return "영화가 즉 삶 그 자체인 '영화 장인'"
        elif viewing_time < 7711:
            return "경지에 도달한 'Film Master'"
        else:
            return None

    def _process_user_rating_response(self, user_id: int, user_rating: UserRating) -> UserRatingResponse:
        return UserRatingResponse(
                id=user_rating.id,
                user_id=user_rating.user_id,
                rating_num=user_rating.rating_num,
                rating_avg=user_rating.rating_avg,
                rating_dist=user_rating.rating_dist,
                rating_mode=user_rating.rating_mode,
                rating_message=user_rating.rating_message,
                viewing_time=user_rating.viewing_time,
                viewing_message=user_rating.viewing_message
                )
