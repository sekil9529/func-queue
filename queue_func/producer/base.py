# coding: utf-8

import abc
import typing as t

from queue_func.message.base import BaseMessage, Packed


class BaseProducer(t.Generic[Packed], metaclass=abc.ABCMeta):

    __slots__ = (
        "_message",
    )

    def __init__(self, message: BaseMessage[Packed]):

        self._message = message

    async def publish(
            self,
            coro_args: tuple[t.Any],
            coro_kwargs: dict[str, t.Any] | None = None,
            **kwargs) -> None:

        message = self._message.pack(coro_args, coro_kwargs)
        await self._publish(message, **kwargs)

    @abc.abstractmethod
    async def _publish(self, data: Packed, **kwargs) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def join(self) -> None:
        pass
