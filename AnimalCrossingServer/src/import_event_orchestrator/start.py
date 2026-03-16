import asyncio
import logging

from import_event_orchestrator import app


def configure_logging() -> None:
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger(
        "import_event_orchestrator.villager_import_orchestrator"
    ).setLevel(logging.DEBUG)


def main() -> None:
    configure_logging()
    asyncio.run(app.execute())


if __name__ == "__main__":
    main()
