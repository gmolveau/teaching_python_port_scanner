from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    # fields
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    # relationships
    posts: Mapped[list["BlogPost"]] = relationship(back_populates="author")
    likes: Mapped[list["Like"]] = relationship(back_populates="user")
    liked_posts: Mapped[list["BlogPost"]] = relationship(
        secondary="likes", back_populates="liked_by"
    )


class BlogPost(Base):
    __tablename__ = "blog_posts"
    # fields
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str]
    # relationships (one-to-many)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")
    # relationships (many-to-many)
    likes: Mapped[list["Like"]] = relationship(back_populates="post")
    liked_by: Mapped[list["User"]] = relationship(
        secondary="likes", back_populates="liked_posts"
    )


class Like(Base):
    __tablename__ = "likes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="likes")
    post: Mapped["BlogPost"] = relationship(back_populates="likes")
