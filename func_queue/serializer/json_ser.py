# coding: utf-8

import json
import typing as t

from func_queue.serializer.utils import default as _default

__all__ = (
    "dumps",
    "loads",
)


def dumps(data: t.Any) -> bytes:

    return json.dumps(data, default=_default).encode("utf-8")


def loads(data: str | bytes) -> t.Any:

    return json.loads(data)
