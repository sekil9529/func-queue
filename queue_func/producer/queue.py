# coding: utf-8

import asyncio

from queue_func.errors import PublishTimeoutError
from queue_func.serializer.base import Message
from queue_func.producer.base import BaseProducer
from queue_func.shared_resource.queue import Resource


class Producer(BaseProducer[Message, Resource]):

    async def _publish(self, msg: Message, *, timeout: float | None) -> None:

        if timeout:
            try:
                await asyncio.wait_for(self._resource.queue.put(msg), timeout)
            except asyncio.TimeoutError as exc:
                raise PublishTimeoutError("publish timed out") from exc
            return None
        await self._resource.queue.put(msg)
