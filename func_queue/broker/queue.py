# coding: utf-8

import asyncio
import typing as t

from func_queue.type import T

from func_queue.broker.base import BaseBroker as _BaseBroker
from func_queue.producer.queue import Producer
from func_queue.consumer.queue import Consumer

if t.TYPE_CHECKING:
    from func_queue.config.queue import Config


class Broker(_BaseBroker[T, "Config"]):

    __slots__ = (
        "_queue",
    )

    PRODUCER_CLS = Producer
    CONSUMER_CLS = Consumer

    def __init__(self, config: "Config"):
        super().__init__(config)
        self._queue: asyncio.Queue[T] = asyncio.Queue(maxsize=self._config.maxsize)

    @property
    def queue(self) -> asyncio.Queue[T]:

        return self._queue
