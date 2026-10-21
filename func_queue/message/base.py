# coding: utf-8

import abc
import typing as t

from func_queue.serializer.base import BaseSerializer

Packed = t.TypeVar("Packed")

type ArgsMessage = tuple[tuple[t.Any], dict[str, t.Any]]


class BaseMessage(t.Generic[Packed], metaclass=abc.ABCMeta):

    __slots__ = (
        "_enable_serializer",
        "_serializer",
    )

    def __init__(
            self,
            message_serializer_cls: type[BaseSerializer],
            enable_serializer: bool):

        self._serializer = message_serializer_cls()
        self._enable_serializer = enable_serializer

    @abc.abstractmethod
    def pack(
            self,
            coro_args: tuple[t.Any],
            coro_kwargs: dict[str, t.Any] | None = None) -> Packed:

        pass

    @abc.abstractmethod
    def unpack(self, message: Packed) -> ArgsMessage:

        pass
