from flask import Blueprint, redirect, render_template, request, url_for

from src.exceptions import NotAuthenticated
from src.services.sessions import get_current_user_id

home_blueprint = Blueprint("home", __name__)


@home_blueprint.get("/")
def home_page():
    try:
        get_current_user_id(request.cookies.get("session_id"))
        return redirect(url_for("dashboard.dashboard_page"))
    except NotAuthenticated:
        return render_template("index.html")
