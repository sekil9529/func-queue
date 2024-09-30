# coding: utf-8

import abc
import typing as t


class BasePoolExecutor(metaclass=abc.ABCMeta):

    __slots__ = (
        "_maxsize",
    )

    def __init__(self, maxsize: int):

        self._maxsize = maxsize

    @abc.abstractmethod
    def submit(self, func: t.Callable[..., t.Any], *args, **kwargs):

        pass

    @abc.abstractmethod
    def join(self) -> None:

        pass
