# coding: utf-8

import typing as t

from queue_func.factory.backend import Backend

if t.TYPE_CHECKING:
    from queue_func.core.broker import BaseBroker

__all__ = (
    "register_backend",
    "build_broker",
)

BrokerBuilder = t.Callable[..., "BaseBroker[t.Any, t.Any]"]

_BUILDERS: dict[Backend, BrokerBuilder] = {}


def register_backend(backend: Backend) -> t.Callable[[BrokerBuilder], BrokerBuilder]:

    def decorator(fn: BrokerBuilder) -> BrokerBuilder:

        if backend in _BUILDERS:
            raise ValueError(f"backend {backend!r} is already registered")
        _BUILDERS[backend] = fn
        return fn

    return decorator


def build_broker(
        backend: Backend,
        coro: t.Callable[..., t.Coroutine],
        **kwargs: t.Any) -> "BaseBroker[t.Any, t.Any]":

    try:
        builder = _BUILDERS[backend]
    except KeyError:
        raise NotImplementedError(f"backend {backend!r} is not implemented yet") from None
    return builder(coro, **kwargs)
