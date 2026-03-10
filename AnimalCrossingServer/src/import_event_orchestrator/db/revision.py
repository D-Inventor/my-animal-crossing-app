import argparse
import tomllib
from pathlib import Path

from alembic import command
from alembic.config import Config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--message", required=True)
    parser.add_argument("--autogenerate", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    pyproject_path = repo_root / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        pyproject = tomllib.load(f)

    migrations_config = pyproject["tool"]["animal_crossing"]["migrations"][
        "import_event_orchestrator"
    ]
    script_location = migrations_config["script_location"]

    alembic_cfg = Config(toml_file=str(pyproject_path))
    alembic_cfg.set_main_option("script_location", str(repo_root / script_location))

    command.revision(
        alembic_cfg,
        message=args.message,
        autogenerate=args.autogenerate,
    )
