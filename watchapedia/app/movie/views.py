from fastapi import APIRouter, Depends, Query
from typing import Annotated, List, Optional
from watchapedia.app.movie.errors import InvalidFormatError
from watchapedia.app.movie.service import MovieService
from watchapedia.app.movie.crawling import MovieChartCrawler
from watchapedia.app.movie.dto.requests import AddMovieRequest, UpdateMovieRequest, AddMovieListRequest
from watchapedia.app.movie.dto.responses import MovieDataResponse

movie_router = APIRouter()

@movie_router.post("", 
                status_code=201,
                summary="영화 추가",
                description="[유저영역 아님] 영화 정보를 받아 DB에 영화를 추가하고 성공 시 저장된 정보를 반환합니다."
)
def add_movie(
    add_movie_request: AddMovieRequest,
    movie_service: Annotated[MovieService, Depends()]
) -> MovieDataResponse:
    return movie_service.add_movie(
        add_movie_request.title, 
        add_movie_request.original_title,
        add_movie_request.year, 
        add_movie_request.synopsis,
        add_movie_request.running_time, 
        add_movie_request.grade,
        add_movie_request.poster_url,
        add_movie_request.backdrop_url,
        add_movie_request.genres,
        add_movie_request.countries,
        add_movie_request.participants
    )

@movie_router.post("",
                status_code=201,
                summary="영화 리스트 추가",
                description="[유저영역 아님] 여러 영화 정보를 받아 DB에 영화들을을 추가하고 성공 시 저장된 정보를 반환합니다. (EC2에서 크롤링이 작동하지 않아 만든 메서드입니다.)")
def add_movie_list(
    add_movie_list_request: list[AddMovieListRequest],
    movie_service: Annotated[MovieService, Depends()]
) -> list[MovieDataResponse]:
    return movie_service.add_movie_list(
        add_movie_list_request
    )

@movie_router.get("/{movie_id}",
                status_code=200,
                summary="영화 조회",
                description="영화 id로 DB를 조회하여 성공 시 영화 정보를 반환합니다.")
def get_movie(
    movie_id: int,
    movie_service: Annotated[MovieService, Depends()]
) -> MovieDataResponse:
    return movie_service.search_movie(movie_id)

@movie_router.patch("/{movie_id}",
                status_code=200,
                summary="영화 정보 업데이트",
                description="특정 영화의 데이터를 업데이트 한 후 성공 시 'Success'를 반환합니다. 업데이트 가능한 항목은 [synopsis, grade, average_rating, poster_url, backdrop_url] 입니다.")
def update_movie(
    movie_id: int,
    update_movie_request: UpdateMovieRequest,
    movie_service: Annotated[MovieService, Depends()]
):
    movie_service.update_movie(
        movie_id,
        update_movie_request.synopsis,
        update_movie_request.grade,
        update_movie_request.average_rating,
        update_movie_request.poster_url,
        update_movie_request.backdrop_url
    )
    return 'Success'

# EC2에서 작동하지 않음
# @movie_router.post("/crawl",
#                 status_code=201,
#                 summary="왓챠피디아 영화 차트 크롤링",
#                 description="[상당 시간 소요] 왓챠피디아 영화 메인 페이지에 뜨는 영화 차트의 영화들을 크롤링해 DB에 저장합니다. 차트 종류는 박스오피스(box_office), 왓챠 구매순위(watcha_buying), 왓챠 Top10(watcha10), 넷플릭스 순위(netflix)가 있습니다. 성공 시 'Success'를 반환합니다.")
# def crawl_movie_chart(
#     movie_service: Annotated[MovieService, Depends()],
#     chart_type: str
# ):
#     allowed_chart_type = {"box_office", "watcha_buying", "watcha10", "netflix"}
#     if chart_type is None or chart_type not in allowed_chart_type:
#         raise InvalidFormatError()
#     crawler = MovieChartCrawler(chart_type, movie_service)
#     crawler.start_crawling()
#     return "Success"

@movie_router.get("",
                status_code=200,
                summary="영화 리스트 조회",
                description="주어진 조건에 따른 영화 리스트를 반환합니다. 가능한 조건은 [제목/차트이름/최소별점/최대별점/장르/국가] 입니다. 장르와 국가는 여러 개 입력할 수 있습니다. 차트 영화 정보는 오름차순으로 제공합니다.")
def search_movie_list(
    movie_service: Annotated[MovieService, Depends()],
    title: str | None = None,
    chart_type: str | None = None,
    min_rating: float | None = None,  
    max_rating: float | None = None,
    genres: list[str] | None = Query(None), 
    countries: list[str] | None = Query(None),
    participant_id: int | None = None
) -> list[MovieDataResponse]:
    return movie_service.search_movie_list(title, chart_type, min_rating, max_rating, genres, countries, participant_id)