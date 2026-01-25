from flask import Flask

from src.routes.auth import auth_blueprint
from src.routes.dashboard import dashboard_blueprint
from src.routes.home import home_blueprint


def create_app():
    app = Flask(__name__)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(auth_blueprint)

    return app
