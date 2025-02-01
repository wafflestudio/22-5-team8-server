from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from sqlalchemy import DateTime
from watchapedia.database.common import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from watchapedia.app.review.models import Review
    from watchapedia.app.comment.models import Comment
    from watchapedia.app.collection.models import Collection, CollectionComment
    from watchapedia.app.analysis.models import UserRating, UserPreference

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    login_id: Mapped[str] = mapped_column(String(50), nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String(100), nullable=True) # 소셜 로그인의 경우 비밀번호가 없을 수 있음
    profile_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status_message: Mapped[str | None] = mapped_column(String(100), nullable=True)
    login_type: Mapped[str] = mapped_column(String(50), nullable=True)
    
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
    collections: Mapped[list["Collection"]] = relationship(
        "Collection", back_populates="user", cascade="all, delete, delete-orphan"
    )
    collection_comments: Mapped[list["CollectionComment"]] = relationship(
        "CollectionComment", back_populates="user", cascade="all, delete, delete-orphan"
    )
    user_rating: Mapped["UserRating"] = relationship("UserRating", back_populates="user", uselist=False)
    user_preference: Mapped["UserPreference"] = relationship("UserPreference", back_populates="user", uselist=False)
    
class BlockedToken(Base):
    __tablename__ = "blocked_token"

    token_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    expired_at: Mapped[datetime] = mapped_column(DateTime)

class Follow(Base):
    __tablename__ = "follow"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    follower_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    following_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='uq_follower_following'),
    )

class UserBlock(Base):
    __tablename__ = "user_block"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    blocker_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    blocked_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint('blocker_id', 'blocked_id', name='uq_blocker_blocked'),
    )
