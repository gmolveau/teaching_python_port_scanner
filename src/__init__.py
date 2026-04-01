import uuid

import structlog
from flask import Flask, request

from src.logging import configure_logging
from src.routes.auth import auth_blueprint
from src.routes.dashboard import dashboard_blueprint
from src.routes.home import home_blueprint


def create_app(debug: bool = False):
    configure_logging(debug=debug)

    app = Flask(__name__)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(auth_blueprint)

    @app.before_request
    def bind_correlation_id():
        structlog.contextvars.clear_contextvars()
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

    return app
