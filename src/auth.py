from flask import Blueprint, render_template, request

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.get("/register")
def home():
    return render_template("register.html")


@auth_blueprint.post("/register")
def post_scan():
    form = request.form.to_dict()
    print(form)
