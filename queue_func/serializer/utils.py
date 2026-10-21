# coding: utf-8

import typing as t
from decimal import Decimal
from datetime import datetime, date


def default(o: t.Any) -> t.Any:

    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, datetime):
        return o.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(o, date):
        return o.strftime("%Y-%m-%d")
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
