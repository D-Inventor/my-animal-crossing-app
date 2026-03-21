import asyncio
import signal
from contextlib import suppress
from typing import Protocol


class LoopLikeProtocol(Protocol):
    def add_signal_handler(self, sig: int, callback: object, *args: object) -> None: ...


async def bootstrap_signals(loop: LoopLikeProtocol, task: asyncio.Task) -> None:

    def handle_signal(sig: int) -> None:
        task.cancel()

    for sig in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(sig, handle_signal, sig)

    with suppress(asyncio.CancelledError):
        await task
