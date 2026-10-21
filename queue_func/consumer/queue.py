# coding: utf-8

import asyncio
import typing as t

from queue_func.message.base import BaseMessage, Packed
from queue_func.pool_executor.base import BasePoolExecutor
from queue_func.consumer.base import BaseConsumer as _BaseConsumer


class Consumer(_BaseConsumer[Packed]):

    __slots__ = (
        "_queue",
        "_consume_timeout",
    )

    def __init__(
            self,
            queue: asyncio.Queue[Packed],
            consume_timeout: float,
            message: BaseMessage[Packed],
            coro: t.Callable[..., t.Coroutine],
            enable_consumer: bool,
            pool_executor_cls: type[BasePoolExecutor],
            pool_maxsize: int):

        super().__init__(
            message,
            coro,
            enable_consumer,
            pool_executor_cls,
            pool_maxsize,
        )
        self._queue = queue
        self._consume_timeout = consume_timeout

    async def _consume(self) -> None:

        while (not self._stop_flag) or (not self._queue.empty()):
            try:
                message: Packed = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=self._consume_timeout,
                )
            except asyncio.TimeoutError:
                continue
            coro_args, coro_kwargs = self._message.unpack(message)
            await self._dispatch(coro_args, coro_kwargs)
            self._queue.task_done()

    async def join(self) -> None:

        await super().join()
        await self._queue.join()
