# coding: utf-8

import typing as t

if t.TYPE_CHECKING:  # pragma: no cover
    pass


class BaseMediator:

    def __init__(self):

        self._producer = None
        self._consumer = None

    def register_producer(self, producer) -> None:

        self._producer = producer

    def register_consumer(self, consumer) -> None:

        self._consumer = consumer

    def producer(self):

        return self._producer

    def consumer(self):

        return self._consumer
