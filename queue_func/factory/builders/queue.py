# coding: utf-8

import typing as t

from queue_func.factory.backend import Backend
from queue_func.factory.registry import register_backend

if t.TYPE_CHECKING:
    from queue_func.broker.base import BaseBroker


@register_backend(Backend.QUEUE)
def build_queue_broker(
        coro: t.Callable[..., t.Coroutine],
        **kwargs: t.Any) -> "BaseBroker[t.Any, t.Any]":

    from queue_func.broker.queue import Broker
    from queue_func.config.queue import Config

    return Broker(Config(coro=coro, **kwargs))
