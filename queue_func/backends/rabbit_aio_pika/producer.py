# coding: utf-8

import asyncio
import typing as t

import aio_pika

from queue_func.backends.rabbit_aio_pika.config import DeliveryMode, ExchangeName
from queue_func.errors import PublishTimeoutError
from queue_func.core.producer import BaseProducer
from queue_func.backends.rabbit_aio_pika.resource import Resource

if t.TYPE_CHECKING:
    from aio_pika.abc import AbstractChannel, AbstractExchange


class Producer(BaseProducer[bytes, Resource]):

    __slots__ = (
        "_exchange_name",
        "_exchange_type",
        "_routing_key",
        "_delivery_mode",
        "_channel",
        "_exchange",
        "_setup_lock",
    )

    def __init__(
            self,
            resource: Resource,
            publish_timeout: float | None,
            exchange_name: ExchangeName | str,
            routing_key: str,
            delivery_mode: DeliveryMode):
        self._exchange_name = exchange_name
        self._routing_key = routing_key
        self._delivery_mode = delivery_mode
        self._channel: "AbstractChannel | None" = None
        self._exchange: "AbstractExchange | None" = None
        self._setup_lock = asyncio.Lock()
        super().__init__(resource, publish_timeout)

    async def _publish(self, msg: bytes, *, timeout: float | None) -> None:

        routing_key = self._routing_key or self._resource.queue_name
        message = aio_pika.Message(msg, delivery_mode=self._delivery_mode)

        await self._ensure_exchange()
        try:
            await self._exchange.publish(message, routing_key=routing_key, timeout=timeout)
        except TimeoutError as exc:
            raise PublishTimeoutError("publish timed out") from exc

    async def _ensure_exchange(self) -> None:

        if self._exchange is not None:
            return None

        async with self._setup_lock:
            if self._exchange is None:
                channel = await self._resource.get_channel()
                await self._resource.declare_queue(channel)
                if self._exchange_name == ExchangeName.DEFAULT:
                    exchange = channel.default_exchange
                else:
                    exchange = await channel.get_exchange(self._exchange_name)
                self._channel, self._exchange = channel, exchange

    async def _release(self) -> None:

        channel = self._channel
        if channel is None:
            return None
        self._channel = None
        self._exchange = None
        await self._resource.close_channel(channel)
        await self._resource.try_close_connection()

    def _register_shutdown(self) -> None:

        self._shutdown.register(self._pub_waiter.wait)
        self._shutdown.register(self._release)
