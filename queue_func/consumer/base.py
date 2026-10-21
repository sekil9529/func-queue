# coding: utf-8

import abc
import asyncio
import logging
import contextlib
import typing as t
from functools import wraps

from queue_func.message.base import BaseMessage, Packed
from queue_func.pool_executor.base import BasePoolExecutor


class BaseConsumer(t.Generic[Packed], metaclass=abc.ABCMeta):

    __slots__ = (
        "_message",
        "_coro",
        "_enable_consumer",
        "_pool_executor",
        "_task",
        "_stop_flag",
        "_logger",
    )

    def __init__(
            self,
            message: BaseMessage[Packed],
            coro: t.Callable[..., t.Coroutine],
            enable_consumer: bool,
            pool_executor_cls: type[BasePoolExecutor],
            pool_maxsize: int):

        self._message = message
        self._coro = coro
        self._enable_consumer = enable_consumer
        self._pool_executor = self._init_pool_executor(pool_executor_cls, pool_maxsize)
        self._task: asyncio.Task | None = None
        self._stop_flag = False
        self._logger = logging.getLogger(__name__)

    def _init_pool_executor(
            self,
            consumer_pool_executor_cls: type[BasePoolExecutor],
            consumer_pool_maxsize: int) -> BasePoolExecutor | None:

        if self._enable_consumer:
            return consumer_pool_executor_cls(consumer_pool_maxsize)
        return None

    def _run_until_stopped(
            self,
            coro: t.Callable[..., t.Awaitable],
            delay: float = 0.02) -> t.Callable[..., t.Coroutine]:

        @wraps(coro)
        async def wrapped(*args, **kwargs) -> None:

            while not self._stop_flag:
                try:
                    await coro(*args, **kwargs)
                except Exception as e:
                    self._logger.exception(e)
                await asyncio.sleep(delay)

        return wrapped

    async def _dispatch(self, coro_args: tuple[t.Any], coro_kwargs: dict[str, t.Any], **_kwargs) -> None:

        assert self._pool_executor is not None, "consumer pool not initialized"
        await self._pool_executor.submit(self._coro, coro_args, coro_kwargs)

    async def consume(self) -> None:

        if self._enable_consumer:
            self._stop_flag = False
            consume_loop = self._run_until_stopped(self._consume)
            self._task = asyncio.create_task(consume_loop())
        return None

    @abc.abstractmethod
    async def _consume(self) -> None:  # pragma: no cover

        pass

    async def stop(self) -> None:

        self._stop_flag = True

    async def join(self) -> None:

        if self._task is not None:
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

        if self._pool_executor is not None:
            await self._pool_executor.join()
