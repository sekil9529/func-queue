# coding: utf-8
import asyncio

from queue_func.serializer.base import BaseSerializer, Message
from queue_func.producer.base import BaseProducer


class Producer(BaseProducer[Message]):

    __slots__ = (
        "_queue",
        "_publish_timeout",
    )

    def __init__(
            self,
            queue: asyncio.Queue[Message],
            publish_timeout: float | None,
            serializer: type[BaseSerializer[Message]]):

        super().__init__(serializer)
        self._queue = queue
        self._publish_timeout = publish_timeout

    async def _publish(self, data: Message, **kwargs) -> None:

        if timeout := self._publish_timeout:
            await asyncio.wait_for(self._queue.put(data), timeout)
            return None
        await self._queue.put(data)
