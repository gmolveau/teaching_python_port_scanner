from sqlalchemy import select

from src.db import get_session
from src.models import User


def user_exists(username: str) -> bool:
    with get_session() as db:
        result = db.scalar(select(User).where(User.username == username))
        return result is not None


def add_user(username: str, password: str) -> None:
    with get_session() as db:
        db.add(User(username=username, password_hash=password))
        db.commit()


def get_user_by_username(username: str) -> dict | None:
    with get_session() as db:
        user = db.scalar(select(User).where(User.username == username))
        if not user:
            return None
        return {"id": user.id, "password_hash": user.password_hash}


def get_user_by_id(user_id: int) -> dict | None:
    with get_session() as db:
        user = db.get(User, user_id)
        if not user:
            return None
        return {"id": user.id, "username": user.username}
