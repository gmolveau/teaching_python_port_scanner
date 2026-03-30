from functools import wraps

from flask import g, redirect, request, url_for

from src.exceptions import NotAuthenticated
from src.services.sessions import get_current_user, get_current_user_id


def login_required(f):
    """Redirect to /login if the user is not authenticated."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return redirect(url_for("auth.login_page"))
        try:
            user_id = get_current_user_id(session_id)
            g.current_user_id = user_id
            return f(*args, **kwargs)
        except NotAuthenticated:
            return redirect(url_for("auth.login_page"))

    return decorated_function


def with_user(f):
    """Pass the current user as a `user` keyword argument to the decorated function. Redirect to /login if the user is not authenticated.

    Usage:
        @with_user
        def my_route(user: User):
            print(user.username)
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return redirect(url_for("auth.login_page"))
        try:
            user = get_current_user(session_id)
            return f(*args, user=user, **kwargs)
        except NotAuthenticated:
            return redirect(url_for("auth.login_page"))

    return decorated_function
