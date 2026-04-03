import asyncio
import logging

from import_worker import app


def configure_logging() -> None:
    logging.basicConfig(level=logging.WARN)
    logging.getLogger("messaging.handler.handler_app").setLevel(logging.INFO)
    logging.getLogger("messaging.handler").setLevel(logging.INFO)
    logging.getLogger("import_worker.app").setLevel(logging.DEBUG)
    logging.getLogger("import_worker.dependencies").setLevel(logging.DEBUG)


def main() -> None:
    configure_logging()
    asyncio.run(app.execute())


if __name__ == "__main__":
    main()
