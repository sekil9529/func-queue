# coding: utf-8

import asyncio

from queue_func.broker.queue import Broker
from queue_func.config.queue import Config

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
async def test_broker_wires_producer_to_consumer_end_to_end():

    calls: list[int] = []

    async def work(value: int):
        calls.append(value)

    config = Config(
        work,
        enable_message_serializer=False,
        consume_timeout=0.05,
        consumer_pool_maxsize=2,
        maxsize=10,
    )
    broker = Broker(config)

    await broker.start_consumer()
    await broker.publish((7,), {})
    await _wait_until(lambda: calls == [7])

    await broker.stop_consumer()
    await broker.join_consumer()

    assert calls == [7]


@run_async
async def test_broker_producer_and_consumer_share_message_instance():

    async def noop():
        return None

    broker = Broker(
        Config(noop, enable_message_serializer=False, consume_timeout=0.05, maxsize=1),
    )

    assert broker.message is broker._message


@run_async
async def test_broker_end_to_end_with_default_serializer():

    sums: list[int] = []

    async def add(a: int, b: int):
        sums.append(a + b)

    config = Config(
        add,
        enable_message_serializer=True,
        consume_timeout=0.05,
        consumer_pool_maxsize=2,
        maxsize=10,
    )
    broker = Broker(config)

    await broker.start_consumer()
    await broker.publish((3, 5), {})
    await _wait_until(lambda: sums == [8])

    await broker.stop_consumer()
    await broker.join_consumer()

    assert sums == [8]
