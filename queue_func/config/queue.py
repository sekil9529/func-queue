# coding: utf-8

import typing as t
from pydantic.dataclasses import dataclass as pyd_dataclass

from queue_func.config.utils import ExtraIgnoreConfig
from queue_func.config.general import Config as _Config
from queue_func.serializer.base import BaseSerializer
from queue_func.serializer.raw import Serializer


@pyd_dataclass(frozen=True, config=ExtraIgnoreConfig)
class Config(_Config):

    ## shared resource
    maxsize: int = 200
    serializer_cls: type[BaseSerializer] = Serializer
