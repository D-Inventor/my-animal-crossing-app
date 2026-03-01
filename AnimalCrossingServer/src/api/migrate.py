from pathlib import Path

from api.db.config import DatabaseSettings


def main() -> None:
    """Run Alembic migrations."""
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config()
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        DatabaseSettings()
        .get_connection_url()
        .render_as_string(hide_password=False)
        .replace("%", "%%"),
    )

    alembic_cfg.set_main_option(
        "script_location", str(Path(__file__).parent / "db" / "alembic")
    )

    command.upgrade(alembic_cfg, "head")
