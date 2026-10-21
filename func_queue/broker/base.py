# coding: utf-8

import abc
import typing as t

from func_queue.message.base import BaseMessage, Packed

if t.TYPE_CHECKING:
    from func_queue.config.general import Config
    from func_queue.producer.base import BaseProducer
    from func_queue.consumer.base import BaseConsumer


ConfigType = t.TypeVar("ConfigType", bound="Config")


class BaseBroker(t.Generic[ConfigType, Packed], metaclass=abc.ABCMeta):
    """一条通道的装配者。

    创建时准备好双方共用的 Message，并持有配置。
    producer 和 consumer 属性只把各自需要的东西交出去。
    之后的发送和接收不再经过 Broker。

    Broker 可以创建并调用 Producer 和 Consumer。
    这两边不回头调用 Broker，也碰不到对方和整份配置。
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
    def producer(self) -> "BaseProducer[Packed]":

        return self._producer

    @property
    def consumer(self) -> "BaseConsumer[Packed]":

        return self._consumer
