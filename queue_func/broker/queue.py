# coding: utf-8

import asyncio
import typing as t

from queue_func.serializer.base import Message
from queue_func.shared_resource.queue import Resource
from queue_func.broker.base import BaseBroker as _BaseBroker
from queue_func.producer.queue import Producer
from queue_func.consumer.queue import Consumer

if t.TYPE_CHECKING:
    from queue_func.config.queue import Config


class Broker(_BaseBroker["Config", Message]):
    """内存队列通道。队列由这里创建，再交给 Producer 和 Consumer。"""

    def __init__(self, config: "Config"):
        resource = Resource(
            serializer_cls=config.serializer_cls,
            maxsize=config.maxsize)
        self._producer = Producer(
            resource=resource,
            publish_timeout=config.publish_timeout,
        )
        self._consumer = Consumer(
            resource=resource,
            coro=config.coro,
            enable_consumer=config.enable_consumer,
            consume_timeout=config.consume_timeout,
            pool_executor_cls=config.consumer_pool_executor_cls,
            pool_maxsize=config.consumer_pool_maxsize,
        )
