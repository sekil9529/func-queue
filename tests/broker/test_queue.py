# coding: utf-8

import asyncio

from func_queue.broker.queue import Broker
from func_queue.config.queue import Config

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

    await broker.consumer.consume()
    await broker.producer.publish((7,), {})
    await _wait_until(lambda: calls == [7])

    await broker.consumer.stop()
    await broker.consumer.join()

    assert calls == [7]


@run_async
async def test_broker_producer_and_consumer_share_message_instance():

    async def noop():
        return None

    broker = Broker(
        Config(noop, enable_message_serializer=False, consume_timeout=0.05, maxsize=1),
    )

    assert broker.producer._message is broker.consumer._message


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

    await broker.consumer.consume()
    await broker.producer.publish((3, 5), {})
    await _wait_until(lambda: sums == [8])

    await broker.consumer.stop()
    await broker.consumer.join()

    assert sums == [8]
