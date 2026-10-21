# coding: utf-8
import asyncio

from func_queue.message.base import BaseMessage, Packed
from func_queue.producer.base import BaseProducer


class Producer(BaseProducer[Packed]):

    __slots__ = (
        "_queue",
        "_publish_timeout",
    )

    def __init__(
            self,
            queue: asyncio.Queue[Packed],
            publish_timeout: float | None,
            message: BaseMessage[Packed]):

        super().__init__(message)
        self._queue = queue
        self._publish_timeout = publish_timeout

    async def _publish(self, data: Packed, **kwargs) -> None:

        if timeout := self._publish_timeout:
            await asyncio.wait_for(self._queue.put(data), timeout)
            return None
        await self._queue.put(data)
