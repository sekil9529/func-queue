# coding: utf-8

import abc
import asyncio
import typing as t


class BasePoolExecutor(metaclass=abc.ABCMeta):

    __slots__ = (
        "_maxsize",
    )

    def __init__(self, maxsize: int):

        self._maxsize = maxsize

    @abc.abstractmethod
    async def submit(self, func: t.Callable[..., t.Coroutine], *args, **kwargs) -> asyncio.Task:

        pass

    @abc.abstractmethod
    async def join(self) -> None:

        pass
