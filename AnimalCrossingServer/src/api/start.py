"""Workspace-local start module for the API (FastAPI).

This module lives inside the `api` package so editors and tooling can find
it.
"""

from .app import app


def main() -> None:
    try:
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception:
        print("uvicorn not installed. Install with: pip install fastapi uvicorn")


if __name__ == "__main__":
    main()
