# coding: utf-8

import json
from datetime import date, datetime
from decimal import Decimal

import pytest

from queue_func.serializer.utils import default


def test_default_encodes_decimal_as_str():

    assert default(Decimal("10.50")) == "10.50"
    assert default(Decimal("0")) == "0"


def test_default_encodes_datetime_with_seconds():

    value = datetime(2026, 10, 18, 22, 42, 7)

    assert default(value) == "2026-10-18 22:42:07"


def test_default_encodes_date_without_time():

    value = date(2026, 10, 18)

    assert default(value) == "2026-10-18"


def test_default_prefers_datetime_over_date():

    value = datetime(2026, 1, 2, 3, 4, 5)

    assert isinstance(value, date)
    assert default(value) == "2026-01-02 03:04:05"


@pytest.mark.parametrize(
    "value",
    [object(), set(), b"bytes", complex(1, 2)],
)
def test_default_raises_type_error_for_unsupported_types(value):

    with pytest.raises(TypeError, match="is not JSON serializable"):
        default(value)


def test_default_works_with_json_dumps():

    payload = {
        "amount": Decimal("1.25"),
        "created_at": datetime(2026, 10, 18, 10, 0, 0),
        "day": date(2026, 10, 18),
    }

    encoded = json.dumps(payload, default=default)

    assert json.loads(encoded) == {
        "amount": "1.25",
        "created_at": "2026-10-18 10:00:00",
        "day": "2026-10-18",
    }
