# coding: utf-8

import asyncio

from queue_func.factory import Backend, QueueFuncRuntime, queue

from tests.helpers import run_async


async def _wait_until(predicate, *, timeout: float = 2.0, interval: float = 0.02) -> None:

    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if predicate():
            return
        await asyncio.sleep(interval)
    raise AssertionError("condition not met before timeout")


@run_async
async def test_runtime_start_order_is_reverse_of_list():

    from types import SimpleNamespace

    order: list[str] = []

    def make_func(name: str):
        async def start_consumer() -> None:
            order.append(name)

        return SimpleNamespace(broker=SimpleNamespace(start_consumer=start_consumer))

    runtime = QueueFuncRuntime([make_func("first"), make_func("second")])  # type: ignore[arg-type]
    await runtime.start()

    assert order == ["second", "first"]


@run_async
async def test_runtime_stop_joins_all_consumers_front_to_back():

    hits_a: list[int] = []
    hits_b: list[int] = []

    @queue(Backend.QUEUE, enable_message_serializer=False, consume_timeout=0.05, maxsize=10)
    async def handler_a(n: int):
        hits_a.append(n)

    @queue(Backend.QUEUE, enable_message_serializer=False, consume_timeout=0.05, maxsize=10)
    async def handler_b(n: int):
        hits_b.append(n)

    runtime = QueueFuncRuntime([handler_a, handler_b])
    await runtime.start()
    await handler_a.push(args=(1,))
    await handler_b.push(args=(2,))
    await _wait_until(lambda: hits_a == [1] and hits_b == [2])

    await runtime.stop()

    assert hits_a == [1]
    assert hits_b == [2]
