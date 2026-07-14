from __future__ import annotations
from datetime import UTC, datetime
from sqlalchemy import DateTime,ForeignKey, Integer, String, Text
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from database import Base
from sqlalchemy import UniqueConstraint

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )
    password_hash: Mapped[str] =mapped_column(
        String(255),
        nullable= False,
    )
    posts: Mapped[list[Post]] = relationship(
       back_populates="author",
    )
    comments: Mapped[list[Comment]] = relationship(
        back_populates="author"
    )
    likes: Mapped[list[Like]] = relationship(
        back_populates="user"
    )

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index = True,
    )
    author: Mapped[User] = relationship(
        back_populates="posts",
    )
    comments: Mapped[list[Comment]] = relationship(
        back_populates="post",
    )
    likes: Mapped[list[Like]] = relationship(
        back_populates="post",
    )

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    author: Mapped[User] = relationship(
        back_populates="comments",
    )
    post: Mapped[Post] = relationship(
        back_populates="comments",
    )

class Like(Base):
    __tablename__ = "likes"
    __table_args__=(
        UniqueConstraint(
            "user_id",
            "post_id",
           name = "uq_user_post_like",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    user_id: Mapped[int] =mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True, 
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
        index=True,
    )
    user: Mapped[User] =relationship(
        back_populates="likes",
    )
    post: Mapped[Post] = relationship(
        back_populates="likes",
)