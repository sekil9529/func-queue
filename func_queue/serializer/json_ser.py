# coding: utf-8

import json
import typing as t

from func_queue.serializer.base import BaseSerializer
from func_queue.utils.encoder import default as _default


class JSONSerializer(BaseSerializer):

    def __init__(self, default: t.Optional[t.Callable[[t.Any], t.Any]] = None):
        self._default = default or _default

    def _dumps_to_str(self, data: t.Any) -> str:

        return json.dumps(data, default=self._default)

    def _dumps_to_bytes(self, data: t.Any) -> bytes:

        return self._dumps_to_str(data).encode("utf-8")

    def loads(self, data: t.Union[str, bytes]) -> t.Any:

        return json.loads(data)
