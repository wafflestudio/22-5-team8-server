from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from typing import Annotated
from watchapedia.app.user.models import User, BlockedToken, Follow, UserBlock
from watchapedia.app.review.models import Review
from watchapedia.app.comment.models import Comment
from watchapedia.app.collection.models import Collection
from passlib.context import CryptContext
from watchapedia.auth.utils import create_hashed_password
from datetime import datetime
from watchapedia.app.user.errors import UserAlreadyExistsError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def add_user(self, username: str, login_id: str, login_password: str) -> None:
        user = User(
            username=username,
            login_id=login_id,
            hashed_pwd=create_hashed_password(login_password) # 암호화된 비밀번호 저장
        )
        self.session.add(user)

    def get_user(self, username: str, login_id: str) -> User | None:
        get_user_query = select(User).filter(
            (User.username == username)
            | (User.login_id == login_id)
            )
        
        return self.session.scalar(get_user_query)
    
    def update_user(self, user_id:int, username: str | None, login_password: str | None, profile_url: str | None, status_message: str | None) -> None:
        user = self.get_user_by_user_id(user_id)
        if username is not None:
            if self.get_user_by_username(username) is not None:
                raise UserAlreadyExistsError()
            user.username = username
        if login_password is not None:
            user.hashed_pwd = create_hashed_password(login_password)
        if profile_url is not None:
            user.profile_url = profile_url
        if status_message is not None:
            user.status_message = status_message

    def follow(self, follower_id: int, following_id: int) -> None:
        follow = Follow(follower_id=follower_id, following_id=following_id)
        self.session.add(follow)

    def unfollow(self, follower_id: int, following_id: int) -> None:
        unfollow_query = select(Follow).filter(
            (Follow.follower_id == follower_id) & (Follow.following_id == following_id)
        )
        unfollow = self.session.scalar(unfollow_query)
        self.session.delete(unfollow)

    def get_followings(self, user_id: int) -> list[User]:
        get_followings_query = select(User).join(Follow, Follow.following_id == User.id).filter(Follow.follower_id == user_id)
        return self.session.scalars(get_followings_query).all()
    
    def get_followers(self, user_id: int) -> list[User]:
        get_followers_query = select(User).join(Follow, Follow.follower_id == User.id).filter(Follow.following_id == user_id)
        return self.session.scalars(get_followers_query).all()
    
    def get_followings_count(self, user_id: int) -> int:
        get_following_count_query = select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
        return self.session.scalar(get_following_count_query)
    
    def get_followers_count(self, user_id: int) -> int:
        get_followers_count_query = select(func.count()).select_from(Follow).where(Follow.following_id == user_id)
        return self.session.scalar(get_followers_count_query)
    
    def get_reviews_count(self, user_id: int) -> int:
        count_query = select(func.count()).select_from(Review).where(Review.user_id == user_id)
        return self.session.scalar(count_query)
    
    def get_comments_count(self, user_id: int) -> int:
        count_query = select(func.count()).select_from(Comment).where(Comment.user_id == user_id)
        return self.session.scalar(count_query)
    
    def get_collections_count(self, user_id: int) -> int:
        count_query = select(func.count()).select_from(Collection).where(Collection.user_id == user_id)
        return self.session.scalar(count_query)

    def get_user_by_login_id(self, login_id: str) -> User | None:
        get_user_query = select(User).filter(User.login_id == login_id)
        return self.session.scalar(get_user_query)
    
    def get_user_by_user_id(self, user_id: int) -> User | None:
        get_user_query = select(User).filter(User.id == user_id)
        return self.session.scalar(get_user_query)
    
    def get_user_by_username(self, username: str) -> User | None:
        get_user_query = select(User).filter(User.username == username)
        return self.session.scalar(get_user_query)
    
    # username으로 복수의 user get. 부분집합 허용.
    def search_user_list(self, username: str) -> list[User] | None:
        get_user_query = select(User).filter(User.username.ilike(f"%{username}%"))
        return self.session.execute(get_user_query).scalars().all()
    
    def block_user(self, blocker_id: int, blocked_id: int) -> None:
        userblock = UserBlock(blocker_id=blocker_id, blocked_id=blocked_id)
        self.session.add(userblock)
        
    def unblock_user(self, blocker_id: int, blocked_id: int) -> None:
        unblock_query = select(UserBlock).filter(
            (UserBlock.blocker_id == blocker_id) & (UserBlock.blocked_id == blocked_id)
        )
        unblock = self.session.scalar(unblock_query)
        self.session.delete(unblock)

    def get_blocked_users(self, user_id: int) -> list[int]:
        get_blocked_users_query = select(UserBlock).filter(UserBlock.blocker_id == user_id)
        return [user_block.blocked_id for user_block in self.session.execute(get_blocked_users_query).scalars().all()]
    
    def is_blocked(self, blocker_id: int, blocked_id: int) -> bool:
        is_blocked_query = select(UserBlock).filter(
            (UserBlock.blocker_id == blocker_id) & (UserBlock.blocked_id == blocked_id)
        )

        return self.session.scalar(is_blocked_query) is not None
    
    def block_token(self, token_id: str, expired_at: datetime) -> None:
        blocked_token = BlockedToken(token_id=token_id, expired_at=expired_at)
        self.session.add(blocked_token)

    def is_token_blocked(self, token_id: str) -> bool:
        print(token_id)
        return (
            self.session.scalar(
                select(BlockedToken).where(BlockedToken.token_id == token_id)
            )
            is not None
        )
    
    def is_following(self, follower_id: int, following_id: int) -> bool:
        follow_query = select(Follow).filter(
            (Follow.follower_id == follower_id) & (Follow.following_id == following_id)
        )
        return self.session.scalar(follow_query) is not None
