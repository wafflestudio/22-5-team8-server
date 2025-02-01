from typing import Annotated
from fastapi import Depends
from watchapedia.app.recommend.dto.responses import RecommendResponse
from watchapedia.app.recommend.errors import NotEnoughRatingError
from watchapedia.app.country.repository import CountryRepository
from watchapedia.app.movie.service import MovieService
from watchapedia.app.movie.models import Movie
from watchapedia.app.country.models import Country
from watchapedia.app.user.service import UserService
from watchapedia.app.participant.service import ParticipantService
from watchapedia.app.review.service import ReviewService

class RecommendService():
    def __init__(self,
            movie_service: Annotated[MovieService, Depends()],
            user_service: Annotated[UserService, Depends()],
            review_service: Annotated[ReviewService, Depends()],
            ) -> None:
        self.movie_service = movie_service
        self.user_service = user_service
        self.review_service = review_service

    def user_average_rating(self, user_id: int) -> int:
        user_review_list = self.review_service.user_reviews(user_id, None, None)

        total_rating = 0
        rating_num = 0

        for review in user_review_list :
            if review.rating is not None and review.rating > 0 :
                total_rating += review.rating
                rating_num += 1

        if rating_num == 0 :
            return -1
        else :
            return total_rating / rating_num

    def pcc(self, user_id: int, user_dict, user_average: int, opp_id: int) -> int:
        movie_list = self.movie_service.search_movie_list("")
        movie_id_list = [movie.id for movie in movie_list]
        opp_average = self.user_average_rating(opp_id)

        opp_review_list = self.review_service.user_reviews(opp_id, None, None)
        opp_dict = {}
        for review in opp_review_list :
            if review.rating is not None and review.rating > 0 :
                opp_dict[review.movie_id] = review.rating

        numer = 0
        user_denom = 0
        opp_denom = 0

        for movie_id in movie_id_list :
            if movie_id in user_dict and movie_id in opp_dict :
                numer += (user_dict[movie_id] - user_average) * (opp_dict[movie_id] - opp_average)
                user_denom += (user_dict[movie_id] - user_average) ** 2
                opp_denom += (opp_dict[movie_id] - opp_average) ** 2

        return numer / (user_denom ** 0.5 * opp_denom ** 0.5 + 0.0000001)

    def get_expected_rating(self, user_id: int):
        user_list = self.user_service.search_user_list("")
        user_id_list = [user.id for user in user_list]
        user_id_list = user_id_list[0:50]
        movie_list = self.movie_service.search_movie_list("")
        movie_list = movie_list[0:50]
        user_average = self.user_average_rating(user_id)

        user_review_list = self.review_service.user_reviews(user_id, None, None)
        user_dict = {}
        for review in user_review_list :
            if review.rating is not None and review.rating > 0 :
                user_dict[review.movie_id] = review.rating

        pcc_dict = {}

        for opp_id in user_id_list :
            pcc_dict[opp_id] = self.pcc(user_id, user_dict, user_average, opp_id)

        expected_dict = {}

        for movie in movie_list :
            if movie.average_rating is None :
                continue

            if user_average < 0 :
                expected_dict[movie.id] = movie.average_rating
                continue

            numer = 0
            denom = 0.0000001

            review = self.review_service.get_review_by_user_and_movie(user_id, movie.id)
            if review is None :
                for u_id in user_id_list :
                    u_average = self.user_average_rating(u_id)
                    if u_id != user_id and u_average >= 0 :
                        denom += abs(pcc_dict[u_id])
                        u_review = self.review_service.get_review_by_user_and_movie(u_id, movie.id)
                        if u_review is not None and u_review.rating is not None and u_review.rating > 0 :
                            numer += pcc_dict[u_id] * (u_review.rating - u_average)
            
                if user_average >= 0 :
                    expected_dict[movie.id] = user_average + (numer / denom)

        return expected_dict

    def high_expected_rating(self, user_id: int, list_size: int) -> list[RecommendResponse]:
        expected_dict = self.get_expected_rating(user_id)

        response_list = []

        if len(expected_dict) > 0 :
            expected_list = sorted(expected_dict.items(), key = lambda x: x[1], reverse=True)
            for expected in expected_list :
                movie = self.movie_service.search_movie(expected[0])
                response_list.append(self._process_recommend_response(movie, expected[1]))

        return response_list[:list_size]

    def high_difference(self, user_id: int, list_size: int) -> list[RecommendResponse]:
        expected_dict = self.get_expected_rating(user_id)
        difference_dict = self.get_expected_rating(user_id)
        response_list = []

        for movie_id in difference_dict :
            movie = self.movie_service.search_movie(movie_id)
            difference_dict[movie_id] -= movie.average_rating
        
        if len(difference_dict) > 0 :
            difference_list = sorted(difference_dict.items(), key = lambda x: x[1], reverse=True)
            for difference in difference_list :
                movie = self.movie_service.search_movie(difference[0])
                response_list.append(self._process_recommend_response(movie, expected_dict[difference[0]]))

        return response_list[:list_size]

    def _process_recommend_response(self, movie: Movie, expected_rating: float) -> RecommendResponse:
        return RecommendResponse(
            movie_id = movie.id,
            title = movie.title,
            year = movie.year,
            countries = [
                country for country in movie.countries
            ],
            expected_rating = expected_rating,
            poster_url = movie.poster_url
        )

