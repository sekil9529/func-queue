# coding: utf-8

import asyncio

import pytest

from queue_func.producer.queue import Producer
from queue_func.serializer.raw import Serializer

from tests.helpers import run_async


@run_async
async def test_producer_publish_puts_packed_message_on_queue():

    queue: asyncio.Queue = asyncio.Queue()
    producer = Producer(queue, publish_timeout=None, serializer=Serializer)

    await producer.publish((1, 2), {"c": 3})

    wire = queue.get_nowait()
    assert Serializer.unpack(wire) == ((1, 2), {"c": 3})


@run_async
async def test_producer_publish_timeout_raises_when_queue_full():

    queue: asyncio.Queue = asyncio.Queue(maxsize=1)
    await queue.put(b"block")
    producer = Producer(queue, publish_timeout=0.05, serializer=Serializer)

    with pytest.raises(asyncio.TimeoutError):
        await producer.publish((), {})


@run_async
async def test_producer_stop_and_join_are_no_ops():

    queue: asyncio.Queue = asyncio.Queue()
    producer = Producer(queue, publish_timeout=None, serializer=Serializer)

    await producer.stop()
    await producer.join()
