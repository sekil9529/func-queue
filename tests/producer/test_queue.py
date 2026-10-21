# coding: utf-8

import asyncio

import pytest

from func_queue.message.general import Message
from func_queue.producer.queue import Producer
from func_queue.serializer.orjson_ser import OrJSONSerializer

from tests.helpers import run_async


def _message(*, enable_serializer: bool = False) -> Message:

    return Message(OrJSONSerializer, enable_serializer=enable_serializer)


@run_async
async def test_producer_publish_puts_packed_message_on_queue():

    queue: asyncio.Queue = asyncio.Queue()
    message = _message()
    producer = Producer(queue, publish_timeout=None, message=message)

    await producer.publish((1, 2), {"c": 3})

    wire = queue.get_nowait()
    assert message.unpack(wire) == ((1, 2), {"c": 3})


@run_async
async def test_producer_publish_with_serializer_produces_bytes():

    queue: asyncio.Queue = asyncio.Queue()
    message = _message(enable_serializer=True)
    producer = Producer(queue, publish_timeout=None, message=message)

    await producer.publish(("x",), {})

    wire = queue.get_nowait()
    assert isinstance(wire, bytes)
    args, kwargs = message.unpack(wire)
    assert tuple(args) == ("x",)
    assert kwargs == {}


@run_async
async def test_producer_publish_timeout_raises_when_queue_full():

    queue: asyncio.Queue = asyncio.Queue(maxsize=1)
    await queue.put(b"block")
    message = _message()
    producer = Producer(queue, publish_timeout=0.05, message=message)

    with pytest.raises(asyncio.TimeoutError):
        await producer.publish((), {})


@run_async
async def test_producer_stop_and_join_are_no_ops():

    queue: asyncio.Queue = asyncio.Queue()
    producer = Producer(queue, publish_timeout=None, message=_message())

    await producer.stop()
    await producer.join()
