import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import redirect, request, url_for
from sqlalchemy import select

from src.db import get_session
from src.models import UserSession
from src.services.users import get_user_by_id

SESSION_LIFETIME = timedelta(minutes=30)


def generate_session_id() -> str:
    return secrets.token_hex(32)


def create_session(user_id: int) -> str:
    session_id = generate_session_id()
    now = datetime.now()

    with get_session() as db:
        db.add(UserSession(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            expires_at=now + SESSION_LIFETIME,
        ))
        db.commit()

    return session_id


def get_session_data(session_id: str) -> dict | None:
    with get_session() as db:
        user_session = db.scalar(
            select(UserSession).where(UserSession.session_id == session_id)
        )

    if not user_session:
        return None

    if datetime.now() > user_session.expires_at:
        delete_session(session_id)
        return None

    return {
        "user_id": user_session.user_id,
        "created_at": user_session.created_at,
        "expires_at": user_session.expires_at,
    }


def delete_session(session_id: str) -> bool:
    with get_session() as db:
        user_session = db.scalar(
            select(UserSession).where(UserSession.session_id == session_id)
        )
        if not user_session:
            return False
        db.delete(user_session)
        db.commit()
        return True


def get_current_user(request) -> dict | None:
    user_id = get_current_user_id(request)
    if not user_id:
        return None
    return get_user_by_id(user_id)


def get_current_user_id(request) -> int | None:
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None

    session = get_session_data(session_id)
    if not session:
        return None

    return session["user_id"]


def login_required(f):
    """Redirect to /login if the user is not authenticated."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user_id(request)
        if not current_user:
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)

    return decorated_function
