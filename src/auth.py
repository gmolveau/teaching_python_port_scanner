from flask import Blueprint, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.get("/register")
def register_page():
    return render_template("register.html")


@auth_blueprint.post("/register")
def post_register():
    form = request.form.to_dict()
    password = form.get("password")
    secure_password = generate_password_hash(password)
    print(secure_password)


@auth_blueprint.get("/login")
def login_page():
    return render_template("login.html")


@auth_blueprint.post("/login")
def post_login():
    form = request.form.to_dict()
    password = form.get("password")
    check_password_hash(secure_password, password)
