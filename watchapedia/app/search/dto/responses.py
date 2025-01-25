from pydantic import BaseModel

class SearchResponse(BaseModel):
    movie_list: list[int] | None
    user_list: list[int] | None
    participant_list: list[int] | None
    collection_list: list[int] | None
    movie_dict_by_genre : dict[str, list[int]]
