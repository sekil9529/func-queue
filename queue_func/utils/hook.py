# coding: utf-8

import asyncio
import inspect
import typing as t


class OnceHooks:
    """一组异步回调，按登记顺序只启动一次。"""

    __slots__ = (
        "_hooks",
        "_task",
        "_lock",
    )

    def __init__(self) -> None:

        self._hooks: list[t.Callable[[], t.Awaitable[None]]] = []
        self._task: asyncio.Task[None] | None = None
        self._lock = asyncio.Lock()

    def register(self, hook: t.Callable[[], t.Awaitable[None]]) -> t.Callable[[], t.Awaitable[None]]:
        """登记。返回原函数，便于当装饰器使用。须在 start 之前登记。"""

        self._hooks.append(hook)
        return hook

    async def start(self, *, prepare: t.Callable[[], t.Awaitable[None] | None] | None = None) -> None:
        """第一次调用先执行 prepare，再创建任务；之后再调用是空操作。"""

        async with self._lock:
            if self._task is None:
                if prepare is not None:
                    result = prepare()
                    if inspect.isawaitable(result):
                        await result
                self._task = asyncio.create_task(self._run())

    async def wait(self) -> None:
        """没触发过就直接返回；触发过就等那一个任务。"""

        if self._task is not None:
            await self._task

    async def _run(self) -> None:
        """按登记顺序 await。前一个抛错，后面的不再执行，异常留在 task 上。"""

        for hook in self._hooks:
            await hook()
