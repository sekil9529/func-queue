# coding: utf-8

import abc
import typing as t

from queue_func.serializer.base import BaseSerializer, Message


class BaseProducer(t.Generic[Message], metaclass=abc.ABCMeta):

    __slots__ = (
        "_serializer",
    )

    def __init__(self, serializer: type[BaseSerializer[Message]]):

        self._serializer = serializer

    async def publish(
            self,
            coro_args: tuple[t.Any],
            coro_kwargs: dict[str, t.Any] | None = None,
            **kwargs) -> None:

        packed = self._serializer.pack(coro_args, coro_kwargs)
        await self._publish(packed, **kwargs)

    @abc.abstractmethod
    async def _publish(self, data: Message, **kwargs) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def join(self) -> None:
        pass
