# coding: utf-8

from pydantic.config import ConfigDict

__all__ = (
    "ExtraIgnoreConfig",
)


ExtraIgnoreConfig = ConfigDict(
    extra="ignore",
    validate_assignment=True,
    arbitrary_types_allowed=True,
    coerce_numbers_to_str=True,
)
