from sqlalchemy import select

from src.db import get_session
from src.exceptions import UserNotFound
from src.models import User


def user_exists(username: str) -> bool:
    with get_session() as db:
        stmt = select(User).where(User.username == username)
        user = db.scalar(stmt)
        return user is not None


def add_user(username: str, password: str) -> None:
    with get_session() as db:
        db.add(User(username=username, password_hash=password))
        db.commit()


def get_user_by_username(username: str) -> User:
    with get_session() as db:
        user = db.scalar(select(User).where(User.username == username))
        if not user:
            raise UserNotFound(username)
        return user


def get_user_by_id(user_id: int) -> User:
    with get_session() as db:
        user = db.get(User, user_id)
        if not user:
            raise UserNotFound(user_id)
        return user
