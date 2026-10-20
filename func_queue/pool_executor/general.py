# coding: utf-8

import asyncio
import typing as t

from func_queue.pool_executor.base import BasePoolExecutor
from func_queue.pool_executor.utils import JoinableSemaphore


class PoolExecutor(BasePoolExecutor):

    __slots__ = (
        "_sem",
    )

    def __init__(self, maxsize: int):
        super().__init__(maxsize)
        self._sem = JoinableSemaphore(self._maxsize)

    async def submit(self, func: t.Callable[..., t.Coroutine], *args, **kwargs) -> asyncio.Task:

        await self._sem.acquire()
        return asyncio.create_task(self._consume(func, *args, **kwargs))

    async def _consume(self, func: t.Callable[..., t.Coroutine], *args, **kwargs):

        try:
            await func(*args, **kwargs)
        finally:
            self._sem.release()

    async def join(self):

        await self._sem.join()
