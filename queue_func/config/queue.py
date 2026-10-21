# coding: utf-8

import typing as t
from pydantic.dataclasses import dataclass as pyd_dataclass

from queue_func.config.utils import ExtraIgnoreConfig
from queue_func.config.general import Config as _Config


@pyd_dataclass(frozen=True, config=ExtraIgnoreConfig)
class Config(_Config):

    # broker
    maxsize: int = 200
