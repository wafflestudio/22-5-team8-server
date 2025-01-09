from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from watchapedia.app.movie.dto.requests import AddParticipantsRequest
from watchapedia.app.movie.service import MovieService
from typing import List, Annotated
from fastapi import Depends
import time
import re
import html

# crawls BoxOffice-charted movies
class MovieChartCrawler:
    def __init__(self, chart_type: str, movie_service: Annotated[MovieService, Depends()]):
        """
        box_office: 박스오피스 순위, 30개 탐색
        watcha_buying: 왓챠 구매 순위, 30개 탐색
        watcha10: 왓챠 Top10, 10개 탐색
        netflix: 넷플릭스 영화화순위, 10개 탐색
        """
        self.driver = None
        self.url = "https://pedia.watcha.com/ko-KR/?domain=movie"
        self.chart_type = chart_type
        self.movie_service = movie_service

        # Selenium WebDriver 설정
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # GUI 없이 실행 (옵션)
        chrome_options.add_argument("--window-size=1920,1080")

        # chrome_options.add_argument("--disable-gpu"); # GPU 가속을 비활성화. 일부 시스템에서 GPU 가속이 문제를 일으킬 수 있으므로 비활성화하는 경우가 있습니다.
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])
        self.driver = webdriver.Chrome(options=chrome_options)

    def start_crawling(self) -> None:
        try:
            self.driver.get(self.url)
            time.sleep(2)
            count = 1

            type_dict = {"box_office": 2, "watcha_buying": 4, "watcha10": 6, "netflix": 8}
            limit_dict = {2: 30, 4: 30, 6: 10, 8: 10, 9: 30}
            
            type_num = type_dict.get(self.chart_type, 0)
            limit = limit_dict.get(type_num, 0)

            if type_num == 0 or limit == 0:
                print("Invalid chart type")
            
            while count <= limit:
                try:
                    # 팝업 창 닫아주기
                    popup_box_close = self.driver.find_elements(By.XPATH, '//*[contains(@id, "modal-container")]/div/div/div[2]/button[1]')
                    # ex)
                    # //*[@id="modal-container-aQSZQfSZFGusIS93bRBoa"]/div/div/div[2]/button[1]
                    if popup_box_close:
                        popup_box_close[0].click()

                    # 영화 박스 클릭
                    movie_box = self.driver.find_element(By.XPATH, f'//*[@id="root"]/div[1]/section/div/section/div[{type_num}]/section/div[1]/ul/li[{count}]/a')
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", movie_box)
                    movie_box.click()
                    # actions = ActionChains(self.driver)
                    # actions.move_to_element(movie_box).click().perform()
                    time.sleep(2)

                    # 필수 항목 (언제나 제공되는 항목)

                    title = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/h1').text
                    original_title = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[1]').text
                    # average_rating = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[2]/section[1]/div[2]/div/div[1]').text
                    year = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[2]').text.split("·")[0].strip()
                    genres = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[2]').text.split("·")[1].strip()
                    countries = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[2]').text.split("·")[2].strip()
                    runtime_and_grade = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[3]').text

                    # 선택 항목 (제공되지 않을 수 있는 항목)
                    # 빈 요소(None) 여부 확인 위해, find_elements 메서드를 써야한다.

                    # 등급grade도 없을 수 있다.
                    # 시놉도 없을 수 있다.
                    synopsis_element = self.driver.find_elements(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[2]/section[3]/p')
                    # 포스터, 배경 이미지 제공하지 않는 경우가 있음
                    poster_url_element = self.driver.find_elements(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[1]/div/div/img')
                    backdrop_url_chunk_elemet = self.driver.find_elements(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[1]')
                    # average_rating 요소가 있는지 확인 - 미개봉 영화는 평균 별점 없음
                    # average_rating_element = self.driver.find_elements(By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[2]/section[1]/div[2]/div/div[1]')
                    # average_rating = self._get_text_if_exists(average_rating_element)
                    
                    runtime_str, grade = self._get_runtime_and_grade_if_exists(runtime_and_grade)
                    backdrop_url_chunk = self._get_url_if_exists(backdrop_url_chunk_elemet, "style")

                    synopsis = self._get_synopsis_if_exists(synopsis_element)
                    running_time = self._convert_runtime_to_minutes(runtime_str)
                    poster_url = self._get_url_if_exists(poster_url_element, "src")
                    backdrop_url = self._get_url_from_chunk(backdrop_url_chunk)
                    genre_list = self._parse_genres(genres)
                    country_list = self._parse_countries(countries)
                    
                    participants_list = self._process_participants()

                    self.movie_service.add_movie(
                        title, original_title, int(year), synopsis, int(running_time), grade, poster_url, backdrop_url, genre_list, country_list, participants_list, self.chart_type, count
                    )

                    # 이전 페이지로 이동
                    self.driver.back()
                    time.sleep(2)
                    count += 1

                except NoSuchElementException as e:
                    # click the next button if there is no such movie element in page
                    print(f"Error due to No Such Element: {e}")
                    time.sleep(2)

                    try:
                        next_button = self.driver.find_elements(By.XPATH, f'//*[@id="root"]/div[1]/section/div/section/div[2]/section/div[{type_num}]/button')
                        # boxoffice button
                        # //*[@id="root"]/div[1]/section/div/section/div[2]/section/div[2]/button'
                        # watcha purchase chart
                        # //*[@id="root"]/div[1]/section/div/section/div[4]/section/div[2]/button
                        # self.driver.execute_script("arguments[0].click();", next_button)
                        if next_button:
                            actions_next = ActionChains(self.driver)
                            actions_next.move_to_element(next_button[0]).click().perform()
                            print('next button clicked')
                        else:
                            print("no next button")
                        time.sleep(2)
                        continue
                    except Exception as e:
                        print(f"Error while clicking next button: {e}")
                        raise e

                except Exception as e:
                    print(f"Error processing movie {count}: {e}")
                    raise e

        except Exception as e:
            print(f"Error during crawling: {e}")
            raise e
        finally:
            self.driver.quit()

    def _get_runtime_and_grade_if_exists(self, runtime_and_grade: str) -> (tuple[str, str | None]):
        if "·" in runtime_and_grade:
            runtime = runtime_and_grade.split("·")[0].strip()
            grade = runtime_and_grade.split("·")[1].strip()
            return runtime, grade
        
        runtime = runtime_and_grade
        grade = None
        return runtime, grade

    def _get_synopsis_if_exists(self, elements: List[WebElement]) -> str | None:
        if elements:
            return elements[0].text.replace("\n", "\\n")    # escape char
        return None
    
    def _get_url_if_exists(self, elements: List[WebElement], attr: str) -> str | None:
        if elements:
            return elements[0].get_attribute(attr)
        return None

    def _parse_genres(self, genres: str) -> list[str]:
        res = []
        for genre in genres.split("/"):
            res.append(genre.strip())
        return res
    
    def _parse_countries(self, countries: str) -> list[str]:
        res = []
        for country in countries.split(","):
            res.append(country.strip())
        return res

    def _get_url_from_chunk(self, chunk: str | None) -> str | None:
        if chunk is None:
            return chunk
        decoded_chunk = html.unescape(chunk)
        pattern = r'url\("(.*?)"\)'
        match = re.search(pattern, decoded_chunk)
        if match:
            return match.group(1)
        return match

    def _convert_runtime_to_minutes(self, runtime_str: str):
        # 기본 값
        total_minutes = 0

        # 시간 추출
        if "시간" in runtime_str:
            hours = int(runtime_str.split("시간")[0].strip())
            total_minutes += hours * 60  # 시간 -> 분 변환

        # 분 추출
        if "분" in runtime_str:
            minutes_part = runtime_str.split("시간")[-1] if "시간" in runtime_str else runtime_str
            minutes = int(minutes_part.replace("분", "").strip())
            total_minutes += minutes

        return total_minutes

    def _process_participants(self) -> list[AddParticipantsRequest]:
        participants_list = []
        count = 1
        while True:
            try:
                name_and_role_elements = self.driver.find_elements(By.XPATH, f'//*[@id="content_credits"]/section/div[1]/ul/li[{count}]/a')

                if not name_and_role_elements:
                    break
                try:
                    name_and_role = name_and_role_elements[0].get_attribute("title")
                    name = name_and_role.split("(")[0].strip()
                    role = name_and_role.split("(")[-1].strip(")")
                    image_url_elements = self.driver.find_elements(By.XPATH, f'//*[@id="content_credits"]/section/div[1]/ul/li[{count}]/a/div[1]/div/div')

                    image_url_chunk = self._get_url_if_exists(image_url_elements, "style")
                    image_url = self._get_url_from_chunk(image_url_chunk)

                    participants_list.append(AddParticipantsRequest(
                        name=name, role=role, profile_url=image_url
                    ))

                    count += 1

                except Exception as e:
                    print(f"Error processing participants: {e}")

            except Exception as e:
                print(f"Error fetching participants: {e}")
        
        return participants_list

