# coding: utf-8
import asyncio
import typing as t

from func_queue.type import T
from func_queue.producer.base import BaseProducer

if t.TYPE_CHECKING:
    from func_queue.config.queue import Config
    from func_queue.broker.queue import Broker


class Producer(BaseProducer[T, "Broker", "Config"]):


    async def _publish(self, data: T | bytes, **kwargs) -> None:

        if timeout := self._config.producer_publish_timeout:
            await asyncio.wait_for(self._broker.queue.put(data), timeout)
        await self._broker.queue.put(data)
