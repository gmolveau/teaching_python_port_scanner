from flask import Blueprint, redirect, render_template, request, url_for

from src.services.sessions import get_current_user

home_blueprint = Blueprint("home", __name__)


@home_blueprint.get("/")
def home_page():
    current_user = get_current_user(request)
    if current_user:
        return redirect(url_for("dashboard.dashboard_page"))
    return render_template("index.html")
