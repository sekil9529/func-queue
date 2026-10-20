# coding: utf-8

import abc
import typing as t

from func_queue.type import T, B, C


class BaseProducer(t.Generic[T, B, C], metaclass=abc.ABCMeta):

    __slots__ = (
        "_broker",
        "_config",
    )

    def __init__(self, broker: B, config: C):

        self._broker = broker
        self._config = config

    def _ensure_data(self, msg: T) -> T | bytes:

        if (dumps := self._config.dumps) is not None:
            return dumps(msg)
        return msg

    async def publish(self, msg: T, **kwargs) -> None:

        data = self._ensure_data(msg)
        await self._publish(data, **kwargs)

    @abc.abstractmethod
    async def _publish(self, data: T | bytes, **kwargs) -> None:

        pass

    async def stop(self) -> None:

        pass

    async def join(self) -> None:

        pass
