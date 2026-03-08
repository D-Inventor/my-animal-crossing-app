import asyncio

from import_event_orchestrator import app


def main() -> None:
    asyncio.run(app.execute())


if __name__ == "__main__":
    main()
