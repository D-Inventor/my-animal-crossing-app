"""Workspace-local start module for the API (FastAPI).

This module lives inside the `api` package so editors and tooling can find
it.
"""

from api.telemetry.config import configure_telemetry

from .app import app


def main() -> None:
    try:
        import uvicorn

        configure_telemetry(app)

        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"Error running uvicorn: {e}")
        print("uvicorn not installed. Install with: pip install fastapi uvicorn")


if __name__ == "__main__":
    main()
