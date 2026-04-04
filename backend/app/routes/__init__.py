from flask import Flask

from .auth import auth_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
