import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import redirect, request, url_for

from src.db import get_connection
from src.services.users import get_user_by_id

SESSION_LIFETIME = timedelta(minutes=30)


def generate_session_id():
    return secrets.token_hex(32)


def create_session(user_id: int) -> str:
    session_id = generate_session_id()
    created_at = datetime.now().isoformat()
    expires_at = (datetime.now() + SESSION_LIFETIME).isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (session_id, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (session_id, user_id, created_at, expires_at),
        )
        conn.commit()

    return session_id


def get_session(session_id: str) -> dict | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, created_at, expires_at FROM sessions WHERE session_id = ?",
            (session_id,),
        )
        result = cursor.fetchone()

    if not result:
        return None

    user_id, created_at, expires_at = result

    # Delete expired session
    if datetime.now() > datetime.fromisoformat(expires_at):
        delete_session(session_id)
        return None

    return {
        "user_id": user_id,
        "created_at": created_at,
        "expires_at": expires_at,
    }


def delete_session(session_id: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_current_user(request) -> dict | None:
    user_id = get_current_user_id(request)
    if not user_id:
        return None
    return get_user_by_id(user_id)


def get_current_user_id(request) -> int | None:
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None

    session = get_session(session_id)
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
