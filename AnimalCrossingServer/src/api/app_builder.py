from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncContextManager, AsyncGenerator, Callable, Self

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from api.db.event_handler import get_event_handler_collection
from api.db.lifespan import set_engine
from api.messagebus.event_publisher import EventPublisher
from api.villagers import router as villagers_router


class AppBuilder:
    def __init__(self) -> None:
        self._lifespan_managers: list[Callable[[FastAPI], AsyncContextManager]] = []

    def add_lifespan_manager(
        self, value: Callable[[FastAPI], AsyncContextManager]
    ) -> Self:
        self._lifespan_managers.append(value)
        return self

    def add_sync_lifespan_function(self, value: Callable[[FastAPI], None]) -> Self:

        @asynccontextmanager
        async def sync_lifespan_wrapper(app: FastAPI) -> AsyncGenerator:
            value(app)
            yield

        self._lifespan_managers.append(sync_lifespan_wrapper)
        return self

    def add_database_engine(self, value: Callable[[], AsyncEngine]) -> Self:
        def factory_wrapper(app: FastAPI) -> None:
            engine = value()
            session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
            set_engine(app, engine, session_maker)

        self.add_sync_lifespan_function(factory_wrapper)
        return self

    def add_message_publisher(
        self, value: Callable[..., AsyncContextManager[AIOKafkaProducer]]
    ) -> Self:
        @asynccontextmanager
        async def add_publisher_and_subscribe(app: FastAPI) -> AsyncGenerator:
            async with value() as kafka_producer:
                publisher = EventPublisher(kafka_producer)
                event_handler = get_event_handler_collection(app)
                event_handler.subscribe(publisher.publish)
                yield

        self.add_lifespan_manager(add_publisher_and_subscribe)
        return self

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> AsyncGenerator:
        async with AsyncExitStack() as stack:
            for manager in self._lifespan_managers:
                await stack.enter_async_context(manager(app))
            yield

    def build(self) -> FastAPI:
        app = FastAPI(title="Animal Crossing API", lifespan=self._lifespan)
        app.include_router(villagers_router)
        return app
