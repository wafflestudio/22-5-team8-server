from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from database.common import Base
from sqlalchemy import DateTime

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    login_id: Mapped[str] = mapped_column(String(50), nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String(100), nullable=True) # 소셜 로그인일 경우 비밀번호가 없으므로 nullable True
    login_type: Mapped[str] = mapped_column(String(50), nullable=True) # 소셜 로그인인지 로컬 로그인인지 구분하기 위한 컬럼
    
class BlockedToken(Base):
    __tablename__ = "blocked_token"

    token_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    expired_at: Mapped[datetime] = mapped_column(DateTime)