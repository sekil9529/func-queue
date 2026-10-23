# coding: utf-8

import abc
import asyncio
import logging
import contextlib
import typing as t
from functools import wraps

from queue_func.serializer.base import Message
from queue_func.core.resource import Resource
from queue_func.pool_executor.base import BasePoolExecutor
from queue_func.utils.hook import OnceHooks


class BaseConsumer(t.Generic[Message, Resource], metaclass=abc.ABCMeta):

    __slots__ = (
        "_resource",
        "_coro",
        "_enable_consumer",
        "_pool_executor",
        "_consume_timeout",
        "_startup",
        "_shutdown",
        "_stopped",
        "_running",
        "_logger",
    )

    def __init__(
            self,
            resource: Resource,
            coro: t.Callable[..., t.Coroutine],
            enable_consumer: bool,
            consume_timeout: float,
            pool_executor_cls: type[BasePoolExecutor],
            pool_maxsize: int):

        self._resource = resource
        self._coro = coro
        self._enable_consumer = enable_consumer
        self._pool_executor = self._init_pool_executor(pool_executor_cls, pool_maxsize)
        self._consume_timeout = consume_timeout
        self._stopped = False
        self._running = asyncio.Event()
        self._startup = OnceHooks()
        self._shutdown = OnceHooks()
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
            fn: t.Callable[..., t.Awaitable],
            delay: float = 0.05) -> t.Callable[..., t.Coroutine]:

        @wraps(fn)
        async def wrapped(*args, **kwargs) -> None:

            while not self._stopped:
                try:
                    await fn(*args, **kwargs)
                except Exception as e:
                    self._logger.exception(e)
                await asyncio.sleep(delay)

        return wrapped

    async def _dispatch(self, coro_args: tuple[t.Any], coro_kwargs: dict[str, t.Any], **_kwargs) -> None:

        assert self._pool_executor is not None, "consumer pool not initialized"
        await self._pool_executor.submit(self._coro, coro_args, coro_kwargs)

    async def consume(self) -> None:

        if self._enable_consumer:
            self._stopped = False
            self._startup.register(self._run_until_stopped(self._consume))
            self._register_shutdown()
            await self._startup.start()
            await self._running.wait()

    def _mark_running(self) -> None:
        """消费者已经开始收消息。``consume`` 等到这里才返回。"""

        self._running.set()

    @abc.abstractmethod
    async def _consume(self) -> None:  # pragma: no cover

        pass

    async def stop(self) -> None:

        await self._shutdown.start(prepare=self._mark_stopped)

    def _mark_stopped(self) -> None:

        self._stopped = True

    async def join(self) -> None:

        await self._shutdown.wait()

    async def _join_pool_executor(self):

        if self._pool_executor is not None:
            await self._pool_executor.join()

    def _register_shutdown(self) -> None:

        self._shutdown.register(self._startup.wait)
        self._shutdown.register(self._join_pool_executor)
