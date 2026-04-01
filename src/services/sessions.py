from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, select

from src.db import get_session
from src.exceptions import (
    NotAuthenticated,
    SessionExpired,
    SessionNotFound,
    UserNotFound,
)
from src.models import Session, User
from src.services.users import get_user_by_id

SESSION_LIFETIME = timedelta(minutes=30)


def create_session(user_id: int) -> str:
    with get_session() as db:
        session = Session(
            user_id=user_id,
            expires_at=datetime.now() + SESSION_LIFETIME,
        )
        db.add(session)
        db.commit()
        return session.external_id.hex


def get_session_data(session_id: UUID) -> Session:
    with get_session() as db:
        user_session = db.scalar(
            select(Session).where(Session.external_id == session_id)
        )

        if not user_session:
            raise SessionNotFound(session_id)

        if datetime.now() > user_session.expires_at:
            delete_session(session_id)
            raise SessionExpired(session_id)

        return user_session


def delete_session(session_id: UUID) -> bool:
    with get_session() as db:
        result = db.execute(delete(Session).where(Session.external_id == session_id))
        db.commit()
        return result.rowcount > 0


def get_current_user(session_id: UUID) -> User:
    user_id = get_current_user_id(session_id)
    try:
        return get_user_by_id(user_id)
    except UserNotFound as e:
        raise NotAuthenticated() from e


def get_current_user_id(session_id: UUID) -> int:
    try:
        session = get_session_data(session_id)
    except (SessionNotFound, SessionExpired) as e:
        raise NotAuthenticated() from e

    return session.user_id
