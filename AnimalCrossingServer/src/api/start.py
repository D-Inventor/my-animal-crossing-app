from api.messagebus.config import configure_messagebus
from api.telemetry.config import configure_telemetry

from .app import create_app


def main() -> None:
    try:
        import uvicorn

        app = create_app()

        configure_telemetry(app)
        configure_messagebus(app)

        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"Error running uvicorn: {e}")
        print("uvicorn not installed. Install with: pip install fastapi uvicorn")


if __name__ == "__main__":
    main()
