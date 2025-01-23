from pydantic import BaseModel
from datetime import datetime
from watchapedia.app.user.models import User

class CollectionCommentResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    profile_url: str | None
    collection_id: int
    content: str
    likes_count: int
    created_at: datetime

