# coding: utf-8

import typing as t

from queue_func.factory.deco import QueueFunc

__all__ = (
    "QueueFuncRuntime",
)


class QueueFuncRuntime:
    """按固定顺序批量启动 / 关闭多个 :class:`QueueFunc`。

    stop：consumer 逐个 stop → join；producer 先全体 stop，再全体 join。
    """

    __slots__ = (
        "_funcs",
    )

    def __init__(self, funcs: t.Iterable[QueueFunc[t.Any, t.Any]]) -> None:

        self._funcs = list(funcs)

    async def start(self) -> None:

        for func in reversed(self._funcs):
            await func.broker.start_consumer()

    async def stop(self) -> None:

        for func in self._funcs:
            await func.broker.stop_consumer()
            await func.broker.join_consumer()

        for func in self._funcs:
            await func.broker.stop_producer()
        for func in self._funcs:
            await func.broker.join_producer()
