# coding: utf-8

import typing as t

from func_queue.type import T, C

if t.TYPE_CHECKING:
    from func_queue.producer.base import BaseProducer
    from func_queue.consumer.base import BaseConsumer


class BaseBroker(t.Generic[T, C]):

    __slots__ = (
        "_config",
    )

    PRODUCER_CLS: t.ClassVar[type["BaseProducer[T]"]]
    CONSUMER_CLS: t.ClassVar[type["BaseConsumer[T]"]]

    def __init__(self, config: C):

        self._config = config

    def producer(self) -> "BaseProducer[T]":

        return self.PRODUCER_CLS(self, self._config)

    def consumer(self) -> "BaseConsumer[T]":

        return self.CONSUMER_CLS(self, self._config)
