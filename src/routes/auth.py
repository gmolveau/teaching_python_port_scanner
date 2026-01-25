from flask import Blueprint, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from src.services.sessions import create_session, delete_session, get_current_user
from src.services.users import add_user, get_user_password, user_exists

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.get("/register")
def register_page():
    current_user = get_current_user(request)
    if current_user:
        return redirect(url_for("dashboard.dashboard_page"))
    return render_template("register.html")


@auth_blueprint.post("/register")
def post_register():
    form = request.form.to_dict()
    username = form.get("username")
    if user_exists(username):
        print("user already exists")
        return redirect(url_for("auth.register_page"))

    password = form.get("password", "")
    secure_password = generate_password_hash(password)
    add_user(username, secure_password)
    return redirect(url_for("auth.login_page"))


@auth_blueprint.get("/login")
def login_page():
    current_user = get_current_user(request)
    if current_user:
        return redirect(url_for("dashboard.dashboard_page"))
    return render_template("login.html")


@auth_blueprint.post("/login")
def post_login():
    form = request.form.to_dict()
    username = form.get("username", "")
    if not user_exists(username):
        return redirect(url_for("auth.login_page"))

    secure_password = get_user_password(username)
    password = form.get("password", "")
    if not check_password_hash(secure_password, password):
        return redirect(url_for("forms.home"))

    # Créer une session pour l'utilisateur
    session_id = create_session(username)

    # Créer la réponse avec le cookie de session
    response = redirect(url_for("dashboard.dashboard_page"))
    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,  # Non accessible via JavaScript
        samesite="Lax",  # Protection CSRF basique
        max_age=86400,  # 1 jour
        secure=True,
    )

    return response


@auth_blueprint.get("/logout")
def logout():
    # Récupérer le session_id depuis le cookie
    session_id = request.cookies.get("session_id")

    if session_id:
        # Supprimer la session côté serveur
        delete_session(session_id)

    # Créer une réponse qui supprime le cookie
    response = redirect(url_for("auth.login_page"))
    response.delete_cookie("session_id")

    return response
