from api.app_builder import AppBuilder
from api.db.session import get_engine_from_configuration
from api.messagebus.producer import get_kafka_lifespan_from_config
from api.telemetry.config import configure_telemetry


def main() -> None:
    import uvicorn

    builder = (
        AppBuilder()
        .add_database_engine(get_engine_from_configuration)
        .add_message_publisher(get_kafka_lifespan_from_config)
        .add_sync_lifespan_function(configure_telemetry)
    )

    app = builder.build()

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
