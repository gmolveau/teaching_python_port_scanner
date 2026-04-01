import structlog
from flask import Blueprint, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from src.exceptions import NotAuthenticated, UserNotFound
from src.services.sessions import create_session, delete_session, get_current_user_id
from src.services.users import add_user, get_user_by_username, user_exists

log = structlog.get_logger(__name__)

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.get("/register")
def register_page():
    if session_id := request.cookies.get("session_id"):
        try:
            get_current_user_id(session_id)
            return redirect(url_for("dashboard.dashboard_page"))
        except NotAuthenticated:
            pass
    return render_template("register.html")


@auth_blueprint.post("/register")
def post_register():
    form = request.form.to_dict()
    username = form.get("username")
    if user_exists(username):
        log.warning("register_username_taken", username=username)
        return redirect(url_for("auth.register_page"))

    password = form.get("password", "")
    secure_password = generate_password_hash(password)
    add_user(username, secure_password)
    return redirect(url_for("auth.login_page"))


@auth_blueprint.get("/login")
def login_page():
    if session_id := request.cookies.get("session_id"):
        try:
            get_current_user_id(session_id)
            return redirect(url_for("dashboard.dashboard_page"))
        except NotAuthenticated:
            pass
    return render_template("login.html")


@auth_blueprint.post("/login")
def post_login():
    form = request.form.to_dict()
    username = form.get("username", "")
    try:
        user = get_user_by_username(username)
    except UserNotFound:
        return redirect(url_for("auth.login_page"))

    password = form.get("password", "")
    if not check_password_hash(user.password_hash, password):
        return redirect(url_for("forms.home"))

    session_id = create_session(user.id)

    response = redirect(url_for("dashboard.dashboard_page"))
    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        samesite="Lax",
        max_age=86400,  # 1 day
        secure=True,
    )

    return response


@auth_blueprint.get("/logout")
def logout():
    session_id = request.cookies.get("session_id")

    if session_id:
        delete_session(session_id)

    response = redirect(url_for("auth.login_page"))
    response.delete_cookie("session_id")

    return response
