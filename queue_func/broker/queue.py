# coding: utf-8

import asyncio
import typing as t

from queue_func.message.base import Packed
from queue_func.broker.base import BaseBroker as _BaseBroker
from queue_func.producer.queue import Producer
from queue_func.consumer.queue import Consumer

if t.TYPE_CHECKING:
    from queue_func.config.queue import Config


class Broker(_BaseBroker["Config", Packed]):
    """内存队列通道。队列由这里创建，再交给 Producer 和 Consumer。"""

    __slots__ = (
        "_queue",
    )

    def __init__(self, config: "Config"):
        self._queue: asyncio.Queue[Packed] = asyncio.Queue(maxsize=config.maxsize)
        super().__init__(config)

    def _create_producer(self) -> Producer[Packed]:

        return Producer(
            queue=self._queue,
            publish_timeout=self._config.publish_timeout,
            message=self._message,
        )

    def _create_consumer(self) -> Consumer[Packed]:

        return Consumer(
            queue=self._queue,
            consume_timeout=self._config.consume_timeout,
            message=self._message,
            coro=self._config.coro,
            enable_consumer=self._config.enable_consumer,
            pool_executor_cls=self._config.consumer_pool_executor_cls,
            pool_maxsize=self._config.consumer_pool_maxsize,
        )
