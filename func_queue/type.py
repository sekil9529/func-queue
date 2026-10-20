# coding: utf-8

import typing as t

if t.TYPE_CHECKING:
    from func_queue.config.general import Config
    from func_queue.broker.base import BaseBroker
    from func_queue.pool_executor.base import BasePoolExecutor


T = t.TypeVar("T")
C = t.TypeVar("C", bound="Config")
B = t.TypeVar("B", bound="BaseBroker")
P = t.TypeVar("P", bound="BasePoolExecutor")
