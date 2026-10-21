# coding: utf-8

import typing as t
from pydantic.dataclasses import dataclass as pyd_dataclass

from func_queue.config.utils import ExtraIgnoreConfig
from func_queue.config.general import Config as _Config


@pyd_dataclass(frozen=True, config=ExtraIgnoreConfig)
class Config(_Config):

    # broker
    maxsize: int = 200
