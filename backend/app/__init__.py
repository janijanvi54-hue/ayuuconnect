"""AYUConnect application package."""

import os

from flask import Flask
from flask_cors import CORS

from .config import get_config
from .extensions import db, jwt, migrate
from .routes import register_blueprints
from .utils.errors import register_error_handlers


def create_app(config_name=None):
    """Application factory.

    :param config_name: one of ``development``, ``testing``, ``production``.
        Defaults to the ``FLASK_ENV`` environment variable.
    """
    app = Flask(__name__)

    config = get_config(config_name)
    app.config.from_object(config)
    app.config["JSON_SORT_KEYS"] = False

    CORS(
        app,
        resources={r"/api/*": {"origins": config.CORS_ORIGINS}},
        supports_credentials=True,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models so they are registered with the metadata that
    # Flask-Migrate / db.create_all() relies on.
    with app.app_context():
        from . import models  # noqa: F401
        from .cli import register_commands

        register_commands(app)

    register_blueprints(app)
    register_error_handlers(app)

    return app