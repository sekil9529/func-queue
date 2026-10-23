# coding: utf-8

import asyncio

from queue_func.serializer.base import Message, BaseSerializer
from queue_func.shared_resource.base import BaseResource as _Base


class Resource(_Base[Message]):

    __slots__ = (
        "_queue",
    )

    def __init__(self, serializer_cls: type[BaseSerializer], maxsize: int) -> None:

        super().__init__(serializer_cls)
        self._queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=maxsize)

    @property
    def queue(self) -> asyncio.Queue[Message]:

        return self._queue
