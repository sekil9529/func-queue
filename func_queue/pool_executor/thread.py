# coding: utf-8

import typing as t
from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor

from func_queue.pool_executor.base import BasePoolExecutor

if t.TYPE_CHECKING:
    from concurrent.futures import Future


class ThreadPoolExecutor(BasePoolExecutor):

    __slots__ = (
        "_pool",
    )

    def __init__(self, maxsize: int):
        super().__init__(maxsize)
        self._pool = _ThreadPoolExecutor(max_workers=self._maxsize)

    def submit(self, func, *args, **kwargs) -> "Future":

        return self._pool.submit(func, *args, **kwargs)

    def join(self) -> None:

        self._pool.shutdown(wait=True, cancel_futures=False)
        return None
