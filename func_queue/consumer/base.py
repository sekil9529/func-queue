# coding: utf-8

import abc
import asyncio
import logging
import typing as t
from functools import wraps

from func_queue.type import T, B, C, P


class BaseConsumer(t.Generic[T, B, C, P], metaclass=abc.ABCMeta):

    __slots__ = (
        "_broker",
        "_config",
        "_pool_executor",
        "_event",
        "_task",
        "_logger",
    )

    def __init__(self, broker: B, config: C):

        self._broker = broker
        self._config = config
        self._pool_executor = self._init_pool_executor()
        self._event = asyncio.Event()
        self._task: asyncio.Task | None = None
        self._logger = logging.getLogger(__name__)
        self._stop_flag = False

    def _init_pool_executor(self) -> P | None:

        if self._config.enable_consumer:
            return self._config.consumer_pool_executor_cls(self._config.consumer_pool_maxsize)
        return None

    def _run_until_stopped(self, delay: float = 0.02) -> t.Callable:

        def wrapper(coro) -> t.Callable:

            @wraps(coro)
            async def wrapped(*args, **kwargs) -> None:

                # start block
                self._event.clear()

                while not self._stop_flag:
                    try:
                        await coro(*args, **kwargs)
                    except Exception as e:
                        self._logger.exception(e)
                    await asyncio.sleep(delay)

                # close block
                self._event.set()

            return wrapped

        return wrapper

    async def _callback(self, message: t.Any, **kwargs) -> None:

        await self._pool_executor.submit(self._config.coro, message)

    async def consume(self) -> None:

        if self._config.enable_consumer:
            self._stop_flag = False
            func = self._run_until_stopped()(self._consume)
            self._task = asyncio.create_task(func())
        return None

    @abc.abstractmethod
    async def _consume(self) -> None:  # pragma: no cover

        pass

    async def stop(self) -> None:

        self._stop_flag = True

    async def join(self) -> None:

        await self._event.wait()

        if self._pool_executor is not None:
            await self._pool_executor.join()
