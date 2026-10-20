# coding: utf-8

import typing as t

import orjson

from func_queue.serializer.utils import default as _default

__all__ = (
    "dumps",
    "loads",
)


def dumps(data: t.Any) -> bytes:

    return orjson.dumps(data, default=_default)


def loads(data: str | bytes) -> t.Any:

    return orjson.loads(data)
