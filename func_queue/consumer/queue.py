# coding: utf-8

import asyncio
import typing as t

from func_queue.type import T, P
from func_queue.consumer.base import BaseConsumer as _BaseConsumer

if t.TYPE_CHECKING:
    from func_queue.config.queue import Config
    from func_queue.broker.queue import Broker


class Consumer(_BaseConsumer[T, "Broker", "Config", P]):

    async def _consume(self) -> None:

        queue = self._broker.queue
        timeout = self._config.consume_timeout
        while (not self._stop_flag) or (not queue.empty()):
            try:
                message: t.Any = await asyncio.wait_for(queue.get(), timeout=timeout)
            except asyncio.TimeoutError:
                continue
            await self._callback(message)

    async def join(self) -> None:

        await self._broker.queue.join()
