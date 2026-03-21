import asyncio
import signal

import pytest

from messaging.handler import bootstrap_signals


class FakeLoop:
    def __init__(self) -> None:
        self._handlers: dict[int, tuple[object, tuple[object, ...]]] = {}

    def add_signal_handler(self, sig: int, callback: object, *args: object) -> None:
        self._handlers[sig] = (callback, args)

    def send_signal(self, sig: int) -> None:
        if sig in self._handlers:
            callback, args = self._handlers[sig]
            callback(*args)


@pytest.mark.asyncio
@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGINT])
async def test_should_cancel_task_on_termination_signal(sig: int):
    # given
    started_event = asyncio.Event()
    task = asyncio.create_task(long_running_job(started_event))
    loop = FakeLoop()
    runner_task = asyncio.create_task(bootstrap_signals(loop, task))
    await started_event.wait()

    # when
    loop.send_signal(sig)
    await runner_task

    # then
    assert task.cancelled()


async def long_running_job(started_event: asyncio.Event) -> None:
    started_event.set()
    await asyncio.sleep(3)
