# coding: utf-8

import abc
import typing as t

from queue_func.message.base import BaseMessage, Packed

if t.TYPE_CHECKING:
    from queue_func.config.general import Config
    from queue_func.producer.base import BaseProducer
    from queue_func.consumer.base import BaseConsumer


ConfigType = t.TypeVar("ConfigType", bound="Config")


class BaseBroker(t.Generic[ConfigType, Packed], metaclass=abc.ABCMeta):
    """一条通道的装配者。

    创建时准备好双方共用的 Message，并持有配置与 Producer/Consumer。
    对外通过 publish、start_consumer 等入口操作；运行期业务逻辑仍在 Producer/Consumer 内完成。
    """

    __slots__ = (
        "_config",
        "_message",
        "_producer",
        "_consumer",
    )

    def __init__(self, config: ConfigType):

        self._config = config
        self._message: BaseMessage[Packed] = self._config.message_cls(
            message_serializer_cls=self._config.message_serializer_cls,
            enable_serializer=self._config.enable_message_serializer,
        )
        self._producer = self._create_producer()
        self._consumer = self._create_consumer()

    @abc.abstractmethod
    def _create_producer(self) -> "BaseProducer[Packed]":

        pass

    @abc.abstractmethod
    def _create_consumer(self) -> "BaseConsumer[Packed]":

        pass

    @property
    def message(self) -> BaseMessage[Packed]:

        return self._message

    async def publish(
            self,
            coro_args: tuple[t.Any, ...],
            coro_kwargs: dict[str, t.Any] | None = None,
            **kwargs: t.Any) -> None:

        await self._producer.publish(coro_args, coro_kwargs, **kwargs)

    async def start_consumer(self) -> None:

        await self._consumer.consume()

    async def stop_consumer(self) -> None:

        await self._consumer.stop()

    async def join_consumer(self) -> None:

        await self._consumer.join()

    async def stop_producer(self) -> None:

        await self._producer.stop()

    async def join_producer(self) -> None:

        await self._producer.join()
