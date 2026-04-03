import asyncio
import logging

from import_event_orchestrator import app


def configure_logging() -> None:
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("messaging.handler.handler_app").setLevel(logging.INFO)
    logging.getLogger("messaging.handler").setLevel(logging.INFO)
    logging.getLogger(
        "import_event_orchestrator.villager_import_orchestrator"
    ).setLevel(logging.DEBUG)
    logging.getLogger("import_event_orchestrator.dependencies").setLevel(logging.DEBUG)


def main() -> None:
    configure_logging()
    asyncio.run(app.execute())


if __name__ == "__main__":
    main()
