# coding: utf-8

import asyncio

from queue_func.consumer.queue import Consumer
from queue_func.pool_executor.general import PoolExecutor
from queue_func.serializer.raw import Serializer

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
async def test_consumer_runs_coro_with_unpacked_args():

    queue: asyncio.Queue = asyncio.Queue()
    received: list[tuple] = []

    async def handler(a, b, *, c):
        received.append((a, b, c))

    consumer = Consumer(
        queue=queue,
        consume_timeout=0.05,
        serializer=Serializer,
        coro=handler,
        enable_consumer=True,
        pool_executor_cls=PoolExecutor,
        pool_maxsize=2,
    )

    await consumer.consume()
    await queue.put(Serializer.pack((1, 2), {"c": 3}))
    await _wait_until(lambda: len(received) == 1)

    await consumer.stop()
    await consumer.join()

    assert received == [(1, 2, 3)]


@run_async
async def test_consumer_disabled_does_not_start_consume_loop():

    queue: asyncio.Queue = asyncio.Queue()

    async def handler():
        raise AssertionError("should not run")

    consumer = Consumer(
        queue=queue,
        consume_timeout=0.05,
        serializer=Serializer,
        coro=handler,
        enable_consumer=False,
        pool_executor_cls=PoolExecutor,
        pool_maxsize=1,
    )

    await consumer.consume()
    assert consumer._task is None
    assert consumer._pool_executor is None


@run_async
async def test_consumer_drains_queue_after_stop():

    queue: asyncio.Queue = asyncio.Queue()
    received: list[int] = []

    async def handler(x):
        received.append(x)

    consumer = Consumer(
        queue=queue,
        consume_timeout=0.05,
        serializer=Serializer,
        coro=handler,
        enable_consumer=True,
        pool_executor_cls=PoolExecutor,
        pool_maxsize=2,
    )

    await consumer.consume()
    await queue.put(Serializer.pack((1,), {}))
    await queue.put(Serializer.pack((2,), {}))
    await _wait_until(lambda: len(received) == 2)

    await consumer.stop()
    await consumer.join()

    assert sorted(received) == [1, 2]
