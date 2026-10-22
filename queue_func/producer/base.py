# coding: utf-8

import abc
import typing as t

from queue_func.serializer.base import BaseSerializer, Message


class BaseProducer(t.Generic[Message], metaclass=abc.ABCMeta):

    __slots__ = (
        "_serializer",
        "_publish_timeout",
    )

    def __init__(
            self,
            serializer: type[BaseSerializer[Message]],
            publish_timeout: float | None):

        self._serializer = serializer
        self._publish_timeout = publish_timeout

    async def publish(
            self,
            coro_args: tuple[t.Any],
            coro_kwargs: dict[str, t.Any] | None = None,
            *,
            timeout: float | None = None) -> None:

        if timeout is None:
            timeout = self._publish_timeout
        packed = self._serializer.pack(coro_args, coro_kwargs)
        await self._publish(packed, timeout=timeout)

    @abc.abstractmethod
    async def _publish(self, data: Message, *, timeout: float | None) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def join(self) -> None:
        pass
