# coding: utf-8
import asyncio

from queue_func.errors import PublishTimeoutError
from queue_func.serializer.base import BaseSerializer, Message
from queue_func.producer.base import BaseProducer


class Producer(BaseProducer[Message]):

    __slots__ = (
        "_queue",
    )

    def __init__(
            self,
            queue: asyncio.Queue[Message],
            publish_timeout: float | None,
            serializer: type[BaseSerializer[Message]]):

        super().__init__(serializer, publish_timeout)
        self._queue = queue

    async def _publish(self, data: Message, *, timeout: float | None) -> None:

        if timeout:
            try:
                await asyncio.wait_for(self._queue.put(data), timeout)
            except asyncio.TimeoutError as exc:
                raise PublishTimeoutError("publish timed out") from exc
            return None
        await self._queue.put(data)
