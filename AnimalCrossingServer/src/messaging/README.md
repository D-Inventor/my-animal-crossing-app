# How to make Kafka message apps

The messaging project contains the base components for creating apps that react to messages from Kafka. A message app with Kafka runs in three steps:
 1. Select which topics to listen to
 1. Assign handlers to handle messages
 1. Start the app


The following example shows a minimal working app:

```python
import asyncio

from messaging.handler import accept_all_messages
from messaging.kafka import KafkaMessageHandlerApp
from messaging import MessageTopic

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


## Sending new messages into Kafka
Two ways exist to send new messages into Kafka: by return values and by context.


### Sending messages by return value
When a handler returns a value, the value is assumed to be a message and will be sent to Kafka. This approach provides the simplest way to send responses by messaging:

```python
from pydantic import BaseModel

from messaging import MessageTopic, message

@message(MessageTopic.VILLAGERS)
class MessageHandledEvent():
    message: str

async def process_message(message: object) -> MessageHandledEvent:
    print("I received a message!")

    # This message will be published to Kafka to MessageTopic.VILLAGERS
    return MessageHandledEvent(message="The message was handled")
```


### Sending messages by context
Alternatively, the handler function can accept a second argument `MessageContext`. This allows multiple messages to be sent from a single handler:

```python
from pydantic import BaseModel

from messaging.handler import MessageContext
from messaging import MessageTopic, message

@message(MessageTopic.VILLAGERS)
class MessageHandledEvent():
    message: str

async def process_message(message: object, context: MessageContext) -> None:
    print("I received a message!")

    # This message will be published to Kafka to MessageTopic.VILLAGERS
    context.publish(MessageHandledEvent(message="The message was handled"))
```


Type hints must be used, as they are required to inject the message and context into the handler. The order is also important: the message always comes first and the context always comes second. The context is optional and can be omitted.


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
To handle only specific messages, a filter can be added. The following example handles only messages that have a property `my_property`:

```python
(
    KafkaMessageHandlerApp("your-group-id")
    .add_handler_func(process_message, lambda msg: hasattr(msg, "my_property"))
)
```


If a handler only processes one specific type of message, a filter is not necessary, as long as the proper type hints are applied. The following handler automatically receives only messages of type `ExampleMessage`:

```python
@message(MessageTopic.VILLAGERS)
class ExampleMessage(BaseModel):
    id: uuid.UUID


# This function only receives messages of type ExampleMessage
async def process_message(message: ExampleMessage):
    print("I just received an ExampleMessage")


(
    KafkaMessageHandlerApp("your-group-id")
    .add_handler_func(process_message)
)
```


To handle all messages, the wildcard filter `accept_all_messages` can be passed:

```python
async def process_message(message: object, context: MessageContext) -> None:
    print("I received a message!")


(
    KafkaMessageHandlerApp("your-group-id")
    .add_handler_func(process_message, accept_all_messages)
)
```


## Multiple handlers
Multiple handlers can be registered. All handlers that match the incoming message by their filter will be invoked in the order in which they are registered:

```python
(
    KafkaMessageHandlerApp("your-group-id")
    .add_handler_func(process_one_message, accept_all_messages)
    .add_handler_func(process_another_message, accept_all_messages)
)
```


In this case, both handlers will handle all messages.


## Dependencies
Handlers are responsible for their own dependencies. This chapter outlines the common patterns for dependency management that are used in this project. Two common types of dependencies exist in an app: Singleton and Scoped. Singleton dependencies are initialized once and reused for every message, living until the app stops. Scoped services are initialized for each message and each handler, and live until the handler has finished handling the message.

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


The generic nature of the handler factory allows for alternative implementations with dependency injection frameworks, as long as the result follows the conventions for handler functions.


## Limitations
Message apps in this project have the following known limitations:


### Not atomic
Messaging is not atomic and dispatch of messages is not guaranteed. It is also not guaranteed that messages are cancelled when an error occurs inside a handler.


### Not optimized for high throughput
Only one message is handled at a time. The app does not run anything concurrently.


### Not optimized for robustness
Handlers are responsible for their own resilience. The app only catches errors and logs them.