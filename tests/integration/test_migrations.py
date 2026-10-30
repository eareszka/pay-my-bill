from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from flask_migrate import downgrade, upgrade
from sqlalchemy import inspect

from app import create_app
from app.extensions import db

MIGRATIONS = str(Path(__file__).resolve().parents[2] / "migrations")


def test_migrations_match_models_and_reverse(tmp_path: Path) -> None:
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'm.db'}"})
    with app.app_context():
        upgrade(directory=MIGRATIONS)
        assert {"users", "posts", "login_attempts", "donations"} <= set(
            inspect(db.engine).get_table_names()
        )
        with db.engine.connect() as conn:
            assert compare_metadata(MigrationContext.configure(conn), db.metadata) == []
        downgrade(directory=MIGRATIONS, revision="base")
        assert not {"users", "posts", "login_attempts", "donations"} & set(
            inspect(db.engine).get_table_names()
        )
        db.engine.dispose()
