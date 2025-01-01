from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from watchapedia.database.connection import get_db_session
from typing import Annotated
from watchapedia.app.user.models import User, BlockedToken
from passlib.context import CryptContext
from watchapedia.app.auth.utils import create_hashed_password
from datetime import datetime
from watchapedia.app.user.errors import UserAlreadyExistsError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository():
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def add_user(self, username: str, login_id: str, login_password: str | None) -> None:
        hasehd_pwd = None
        login_type = 'social'
        if login_password is not None:
            hasehd_pwd = create_hashed_password(login_password)
            login_type = 'local'
        user = User(
            username=username,
            login_id=login_id,
            hashed_pwd=hasehd_pwd, # 암호화된 비밀번호 저장
            login_type=login_type
        )
        self.session.add(user)

    def get_user(self, username: str, login_id: str) -> User | None:
        get_user_query = select(User).filter(
            (User.username == username)
            | (User.login_id == login_id)
            )
        
        return self.session.scalar(get_user_query)
    
    def update_user(self, user_id:int, username: str | None, login_password: str | None) -> None:
        user = self.get_user_by_user_id(user_id)
        if username is not None:
            if self.get_user_by_username(username) is not None:
                raise UserAlreadyExistsError()
            user.username = username
        if login_password is not None:
            user.hashed_pwd = create_hashed_password(login_password)

    def get_user_by_login_id(self, login_id: str) -> User | None:
        get_user_query = select(User).filter(User.login_id == login_id)
        return self.session.scalar(get_user_query)
    
    def get_user_by_user_id(self, user_id: int) -> User | None:
        get_user_query = select(User).filter(User.id == user_id)
        return self.session.scalar(get_user_query)
    
    def get_user_by_username(self, username: str) -> User | None:
        get_user_query = select(User).filter(User.username == username)
        return self.session.scalar(get_user_query)
    
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