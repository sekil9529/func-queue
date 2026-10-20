# coding: utf-8

import typing as t
from pickle import NONE

from pydantic.dataclasses import dataclass as pyd_dataclass

from func_queue.config.utils import ExtraIgnoreConfig
from func_queue.serializer.orjson_ser import dumps, loads
from func_queue.pool_executor.base import BasePoolExecutor
from func_queue.pool_executor.general import PoolExecutor


@pyd_dataclass(frozen=True, config=ExtraIgnoreConfig)
class Config:

    coro: t.Callable[[...], t.Coroutine]
    dumps: t.Callable[[t.Any], bytes] | None = dumps
    loads: t.Callable[[str | bytes], t.Any] | None = loads
    enable_consumer: bool = True
    consume_timeout: float = 2.0
    consumer_pool_executor_cls: type[BasePoolExecutor] = PoolExecutor
    consumer_pool_maxsize: int = 200
    publish_timeout: float | None = None
