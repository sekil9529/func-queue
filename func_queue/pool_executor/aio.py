# coding: utf-8

import asyncio
import typing as t

from func_queue.pool_executor.base import BasePoolExecutor


class JoinableSemaphore(asyncio.Semaphore):

    __slots__ = (
        "_maxsize",
        "_event",
    )

    def __int__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self._maxsize = self._value
        self._event = asyncio.Event()

    async def acquire(self):

        status = await super().acquire()
        self._event.clear()
        return status

    def release(self):

        super().release()
        if self._value == self._maxsize:
            self._event.set()

    async def join(self):

        await self._event.wait()


class AioPoolExecutor(BasePoolExecutor):

    __slots__ = (
        "_sem",
    )

    def __init__(self, maxsize: int):
        super().__init__(maxsize)
        self._sem = JoinableSemaphore(self._maxsize)

    async def submit(self, func: t.Callable[..., t.Coroutine], *args, **kwargs):

        await self._sem.acquire()
        await asyncio.gather(self._consume(func, *args, **kwargs))

    async def _consume(self, func: t.Callable[..., t.Coroutine], *args, **kwargs):

        try:
            await func(*args, **kwargs)
        finally:
            self._sem.release()

    async def join(self):

        await self._sem.join()
