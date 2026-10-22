# coding: utf-8

import typing as t

from pydantic.dataclasses import dataclass as pyd_dataclass

from queue_func.config.utils import ExtraIgnoreConfig
from queue_func.serializer.base import BaseSerializer
from queue_func.serializer.orjson_ser import Serializer
from queue_func.pool_executor.base import BasePoolExecutor
from queue_func.pool_executor.general import PoolExecutor


@pyd_dataclass(frozen=True, config=ExtraIgnoreConfig)
class Config:

    # consumer
    coro: t.Callable[[...], t.Coroutine]
    enable_consumer: bool = True
    consume_timeout: float = 2.0
    consumer_pool_executor_cls: type[BasePoolExecutor] = PoolExecutor
    consumer_pool_maxsize: int = 200

    # broker
    serializer_cls: type[BaseSerializer] = Serializer

    # producer
    publish_timeout: float | None = None
