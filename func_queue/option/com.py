# coding: utf-8

import typing as t

from func_queue.serializer.orjson_ser import OrJSONSerializer

if t.TYPE_CHECKING:  # pragma: no cover
    from func_queue.serializer.base import BaseSerializer

__all__ = (
    "CommonOption",
)

_T = t.TypeVar("_T")


class CommonOption:

    def __init__(self,
                 name: str,
                 func: t.Callable,
                 serializer_cls: t.Type["BaseSerializer"] = OrJSONSerializer,
                 disable_serializer: bool = False):

        self._name = name
        self._func = func
        self._serializer = serializer_cls()
        self._disable_serializer = disable_serializer

    @property
    def name(self) -> str:

        return self._name

    @property
    def func(self) -> t.Callable:

        return self._func

    def ensure_dumps(self, data: "_T", return_bytes: bool = False) -> t.Union["_T", str, bytes]:

        if self._disable_serializer:
            return data
        return self._serializer.dumps(data, return_bytes=return_bytes)

    def ensure_loads(self, data: t.Any) -> t.Any:

        if self._disable_serializer:
            return data
        return self._serializer.loads(data)
