# coding: utf-8

import abc
import typing as t

__all__ = (
    "BaseSerializer",
)


class BaseSerializer(metaclass=abc.ABCMeta):

    @t.overload
    def dumps(self, data: t.Any, return_bytes: t.Literal[True]) -> bytes: ...
    @t.overload
    def dumps(self, data: t.Any, return_bytes: t.Literal[False]) -> str: ...
    @t.overload
    def dumps(self, data: t.Any, return_bytes: bool) -> t.Union[str, bytes]: ...

    def dumps(self, data: t.Any, return_bytes: bool = False) -> t.Union[str, bytes]:

        if return_bytes:
            return self._dumps_to_bytes(data)
        return self._dumps_to_str(data)

    @abc.abstractmethod
    def _dumps_to_str(self, data: t.Any) -> str:
        pass

    @abc.abstractmethod
    def _dumps_to_bytes(self, data: t.Any) -> bytes:

        pass

    @abc.abstractmethod
    def loads(self, data: t.Any) -> t.Any:

        pass
