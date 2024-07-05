# coding: utf-8

import typing as t

import orjson

from func_queue.serializer.base import BaseSerializer
from func_queue.utils.encoder import default as _default

__all__ = (
    "OrJSONSerializer",
)


class OrJSONSerializer(BaseSerializer):

    def __init__(self, default: t.Optional[t.Callable[[t.Any], t.Any]] = None):
        self._default = default or _default

    def _dumps_to_str(self, data: t.Any) -> str:

        return self._dumps_to_bytes(data).decode("utf-8")

    def _dumps_to_bytes(self, data: t.Any) -> bytes:

        return orjson.dumps(data, default=self._default)

    def loads(self, data: t.Union[str, bytes]) -> t.Any:

        return orjson.loads(data)
