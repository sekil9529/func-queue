# coding: utf-8

import typing as t

from pydantic.dataclasses import dataclass as pyd_dataclass

from func_queue.config.utils import ExtraIgnoreConfig
from func_queue.message.base import BaseMessage
from func_queue.message.general import Message
from func_queue.serializer.base import BaseSerializer
from func_queue.serializer.orjson_ser import OrJSONSerializer
from func_queue.pool_executor.base import BasePoolExecutor
from func_queue.pool_executor.general import PoolExecutor


@pyd_dataclass(frozen=True, config=ExtraIgnoreConfig)
class Config:

    # consumer
    coro: t.Callable[[...], t.Coroutine]
    enable_consumer: bool = True
    consume_timeout: float = 2.0
    consumer_pool_executor_cls: type[BasePoolExecutor] = PoolExecutor
    consumer_pool_maxsize: int = 200

    # broker
    message_cls: type[BaseMessage] = Message
    message_serializer_cls: type[BaseSerializer] = OrJSONSerializer
    enable_message_serializer: bool = True

    # producer
    publish_timeout: float | None = None
