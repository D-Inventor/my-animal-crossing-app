# How to make Kafka message apps
The messaging project contains the base components for creating apps that react to messages from kafka. A message app with kafka runs in three steps:
 1. Decide which topics to listen to
 1. Assign handlers to handle messages
 1. Start the app

The following example shows a minimal working app:

```python
import asyncio

from messaging.handler.handler_endpoint import accept_all_messages
from messaging.kafka.kafka_message_handler_app import KafkaMessageHandlerApp
from messaging.topics import MessageTopic

async def run_message_app():
    app = (
        KafkaMessageHandlerApp("your-group-id")
        .add_topics([MessageTopic.VILLAGERS])
        .add_handler_func(process_message, accept_all_messages)
    )

    await app.run()

async def process_message(message: object):
    print("I received a message!")

if __name__ == "__main__":
    asyncio.run(run_message_app())
```

## Send new messages into kafka
The app has two ways to send new messages into kafka: by return values and by context.

### Send messages by return value
When a handler returns a value, it is assumed to be a message and will be sent to kafka. This is the easiest way to send responses by messaging:

```python
from pydantic import BaseModel

from messaging.topics import MessageTopic, map_to_topic

@map_to_topic(MessageTopic.VILLAGERS)
class MessageHandledEvent():
    message: str

async def process_message(message: object) -> MessageHandledEvent:
    print("I received a message!")

    # This message will be published to kafka to MessageTopic.VILLAGERS
    return MessageHandledEvent(message="The message was handled")
```

### Send messages by context
Alternatively, you can make the handler function accept a second argument `MessageContext`. This allows you to send multiple messages from a single handler:

```python
from pydantic import BaseModel

from messaging.handler.handler_endpoint import MessageContext
from messaging.topics import MessageTopic, map_to_topic

@map_to_topic(MessageTopic.VILLAGERS)
class MessageHandledEvent():
    message: str

async def process_message(message: object, context: MessageContext) -> None:
    print("I received a message!")

    # This message will be published to kafka to MessageTopic.VILLAGERS
    context.publish(MessageHandledEvent(message="The message was handled"))
```

Make sure that you use the type hints. The type hints are used to inject the message and context into the handler. The order is also important: the message always comes first and the context always comes second. The context is optional and can be omitted.

## Conventions for handlers
A handler is a function that matches one of the following type descriptions:

```python
T = TypeVar('T')

HandlerFunction = Callable[[T], None | object]
    | Callable[[T, MessageContext], None | object]

AsyncHandlerFunction = Callable[[T], Awaitable[None | object]]
    | Callable[[T, MessageContext], Awaitable[None | object]]
```

The type T can be any type of message or `object`.

## Filtering
If you're only interested in specific messages, you can add a filter. The following example only handles messages that have a property `my_property`:

```python
(
    KafkaMessageHandlerApp("your-group-id")
    .add_handler_func(process_message, lambda msg: hasattr(msg, "my_property"))
)
```

If your handler only handles one specific type of message, a filter is not necessary, as long as you apply the proper type hints. The following handler automatically receives only messages of type `ExampleMessage`:

```python
@map_to_topic(MessageTopic.VILLAGERS)
class ExampleMessage(BaseModel):
    id: uuid.UUID

# 👇 This function only receives messages of type ExampleMessage
async def process_message(message: ExampleMessage):
    print("I just received an ExampleMessage")


(
    KafkaMessageHandlerApp("your-group-id")
    .add_handler_func(process_message)
)
```

If your handler can handle all messages, you can pass the wildcard filter `accept_all_messages`:

```python
async def process_message(message: object, context: MessageContext) -> None:
    print("I received a message!")


(
    KafkaMessageHandlerApp("your-group-id")
    .add_handler_func(process_message, accept_all_messages)
)
```

## Multiple handlers
You can register multiple handlers. All handlers that match the incoming message by their filter will be invoked in the order in which they are registered:

```python
(
    KafkaMessageHandlerApp("your-group-id")
    .add_handler_func(process_one_message, accept_all_messages)
    .add_handler_func(process_another_message, accept_all_messages)
)
```

In this case, both handlers will handle all messages.

## Dependencies
The handler is responsible for its own dependencies. This chapter outlines the common patterns for dependency management that are used in this project. There are two common types of dependencies in an app: Singleton and Scoped. Singleton dependencies are initialized once and reused for every message. They live until the app stops. Scoped services are initialized for each message and each handler and live until the handler has finished handling the message.

The following example demonstrates both types of dependencies and demonstrates how the lifetime of each dependency is managed.

```python
# The database engine is a singleton: it lives as long as the whole app
@asynccontextmanager
async def create_engine() -> AsyncGenerator[async_sessionmaker, Any, None]:
    engine = create_async_engine(DatabaseSettings().get_connection_url(), echo=False)
    logger.debug("Engine created")
    yield async_sessionmaker(bind=engine, expire_on_commit=False)

    await engine.dispose()
    logger.debug("Engine disposed")

# The session is scoped: it is created for each incoming message and for each handler individually
@asynccontextmanager
async def create_session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, Any, None]:
    async with session_maker() as session:
        logger.debug("Session created")
        yield session
    logger.debug("Session disposed")


async def run_message_app():
    async with AsyncExitStack() as stack:

        # The singleton dependency is created alongside the app
        # AsyncExitStack makes it easy to manage the lifetime of multiple singleton dependencies
        session_maker = await stack.enter_async_context(create_engine())

        app = (
            KafkaMessageHandlerApp("your-group-id")
            .add_handler_func(create_message_processor(session_maker), accept_all_messages)
        )

        await app.run()

def create_message_processor(session_maker: async_sessionmaker[AsyncSession]):

    # Scoped dependencies are managed in a factory:
    # The factory returns a new handler function that wraps around the actual function
    # The wrapper is responsible for managing the lifetime of scoped services
    # The factory may receive singleton dependencies where necessary
    # The wrapper should follow the conventions for handler functions
    async def handler(message: object) -> None:
        with create_session(session_maker) as session:
            await process_message(message, session)

    return handler

async def process_message(message: object, session: AsyncSession):
    print("I received a message!")

if __name__ == "__main__":
    asyncio.run(run_message_app())
```

Notice the generic nature of the handler factory. Alternative implementations are possible with dependency injection frameworks as long as the result follows the conventions for handler functions.

## Limitations
Message apps in this project have the following known limitations:

### Not atomic
Messaging is not atomic and dispatch of messages is not guaranteed. It is also not guaranteed that messages are cancelled when an error occurs inside a handler.

### Not optimized for high throughput
Though the message app is optimized for async, it only handles one message at a time. The app does not run anything concurrently.

### Not optimized for robustness
Handlers are responsible for their own resilience. The app only catches errors and logs them.