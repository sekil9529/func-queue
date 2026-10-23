# coding: utf-8

import asyncio
import typing as t

from queue_func.serializer.base import Message
from queue_func.backends.queue.resource import Resource
from queue_func.pool_executor.base import BasePoolExecutor
from queue_func.core.consumer import BaseConsumer as _BaseConsumer


class Consumer(_BaseConsumer[Message, Resource]):

    async def _consume(self) -> None:

        while (not self._stopped) or (not self._resource.queue.empty()):
            self._mark_running()
            try:
                message: Message = await asyncio.wait_for(
                    self._resource.queue.get(),
                    timeout=self._consume_timeout,
                )
            except asyncio.TimeoutError:
                continue
            coro_args, coro_kwargs = self._resource.serializer.unpack(message)
            await self._dispatch(coro_args, coro_kwargs)
            self._resource.queue.task_done()

    def _register_shutdown(self) -> None:

        self._shutdown.register(self._startup.wait)
        self._shutdown.register(self._resource.queue.join)
        self._shutdown.register(self._join_pool_executor)
