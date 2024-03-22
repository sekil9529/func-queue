# coding: utf-8

from abc import ABCMeta, abstractmethod


class BasePoolExecutor(metaclass=ABCMeta):

    __slots__ = (
        "_maxsize",
    )

    def __init__(self, maxsize: int):

        self._maxsize = maxsize

    def submit(self, *args, **kwargs) -> :