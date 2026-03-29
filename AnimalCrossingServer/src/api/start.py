from api.app_builder import AppBuilder
from api.db.lifespan import engine_lifespan_from_configuration
from api.telemetry.lifespan import telemetry_lifespan
from messaging.kafka import create_kafka_producer


def main() -> None:
    import uvicorn

    builder = (
        AppBuilder()
        .add_database_engine(engine_lifespan_from_configuration)
        .add_message_publisher(create_kafka_producer)
        .add_sync_lifespan_function(telemetry_lifespan)
    )

    app = builder.build()

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
