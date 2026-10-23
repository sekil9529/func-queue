# coding: utf-8

import abc
import typing as t

from queue_func.shared_resource.base import Resource
from queue_func.serializer.base import Message
from queue_func.utils.hook import OnceHooks
from queue_func.utils.waiter import IdleWaiter


class BaseProducer(t.Generic[Message, Resource], metaclass=abc.ABCMeta):

    __slots__ = (
        "_resource",
        "_publish_timeout",
        "_stopped",
        "_shutdown",
        "_pub_waiter",
    )

    def __init__(
            self,
            resource: Resource,
            publish_timeout: float | None):

        self._resource = resource
        self._publish_timeout = publish_timeout
        self._stopped = False
        self._shutdown = OnceHooks()
        self._pub_waiter = IdleWaiter()
        self._register_shutdown()

    async def publish(
            self,
            coro_args: tuple[t.Any],
            coro_kwargs: dict[str, t.Any] | None = None,
            *,
            timeout: float | None = None) -> None:


        if self._stopped:
            raise RuntimeError("publish called on already stopped")

        if timeout is None:
            timeout = self._publish_timeout
        packed = self._resource.serializer.pack(coro_args, coro_kwargs)
        async with self._pub_waiter.hold():
            await self._publish(packed, timeout=timeout)

    @abc.abstractmethod
    async def _publish(self, msg: Message, *, timeout: float | None) -> None:
        pass

    async def stop(self) -> None:

        await self._shutdown.start(prepare=self._mark_stopped)

    def _mark_stopped(self) -> None:

        self._stopped = True

    async def join(self) -> None:

        await self._shutdown.wait()

    def _register_shutdown(self):

        self._shutdown.register(self._pub_waiter.wait)
