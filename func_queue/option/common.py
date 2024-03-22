# coding: utf-8

import typing as t

import orjson

from func_queue.utils.encoder import default


class CommonOption:

    def __init__(self,
                 name: str,
                 func: t.Callable,
                 json_cls: t.Type = orjson,
                 json_default: t.Callable[[t.Any], t.Any] = default
                 ):

        self._name = name
        self._func = func
        self._json_cls = json_cls
        self._json_default = json_default
