from sqlalchemy import Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from watchapedia.database.common import Base
from sqlalchemy import DateTime

class Comment(Base):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="comments")

    review_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("review.id", ondelete="CASCADE"), nullable=False
    )
    review: Mapped["Review"] = relationship("Review", back_populates="comments")

class UserLikesComment(Base):
    __tablename__ = 'user_likes_comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )
    comment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("comment.id"), nullable=False
    )
