# coding: utf-8

import typing as t

from func_queue.message.base import ArgsMessage, BaseMessage

type PackedMessage = ArgsMessage | bytes


class Message(BaseMessage[PackedMessage]):

    __slots__ = ()

    def pack(
            self,
            coro_args: tuple[t.Any],
            coro_kwargs: dict[str, t.Any] | None = None) -> PackedMessage:

        if coro_kwargs is None:
            coro_kwargs = {}
        message: ArgsMessage = (coro_args, coro_kwargs)
        if self._enable_serializer:
            return self._serializer.dumps(message, return_bytes=True)
        return message

    def unpack(self, message: PackedMessage) -> ArgsMessage:

        if self._enable_serializer:
            return t.cast(ArgsMessage, self._serializer.loads(message))
        return t.cast(ArgsMessage, message)
