import click
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.extensions import celery, db, jwt, migrate


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}})

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app import models  # noqa: F401
    from app.api import register_blueprints
    from app.api.properties import register_media_route

    register_blueprints(app)
    register_media_route(app)

    @app.cli.command("create-operator")
    @click.option("--email", prompt=True)
    @click.option("--name", prompt="Full name")
    @click.option(
        "--role",
        type=click.Choice(["FIELD_AGENT", "ADMIN", "FINANCIAL_PARTNER"]),
        prompt=True,
    )
    def create_operator(email: str, name: str, role: str) -> None:
        from sqlalchemy import select

        from app.models import Role, User

        normalized_email = email.strip().lower()
        if db.session.scalar(select(User.id).where(User.email == normalized_email)):
            raise click.ClickException("An account with this email already exists")
        password = click.prompt("Temporary password", hide_input=True, confirmation_prompt=True)
        if len(password) < 12:
            raise click.ClickException("Password must contain at least 12 characters")
        user = User(email=normalized_email, full_name=name.strip(), role=Role(role))
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Created {role} operator {normalized_email}")

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.errorhandler(404)
    def not_found(_: Exception) -> tuple[dict[str, str], int]:
        return jsonify(error="Resource not found"), 404

    @app.errorhandler(413)
    def request_too_large(_: Exception) -> tuple[dict[str, str], int]:
        return jsonify(error="Upload exceeds the configured size limit"), 413

    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Africa/Accra",
        enable_utc=True,
    )
    celery.conf.update(task_ignore_result=True)
    celery.Task = _make_flask_task(app)
    return app


def _make_flask_task(app: Flask) -> type:
    class FlaskTask(celery.Task):
        abstract = True

        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    return FlaskTask
