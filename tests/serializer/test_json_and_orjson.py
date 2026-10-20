# coding: utf-8

from datetime import date, datetime
from decimal import Decimal

import pytest

from func_queue.serializer import json_ser, orjson_ser


SERIALIZERS = (json_ser, orjson_ser)


@pytest.mark.parametrize("ser", SERIALIZERS)
def test_dumps_default_returns_bytes(ser):

    encoded = ser.dumps({"a": 1})

    assert isinstance(encoded, bytes)
    assert ser.loads(encoded) == {"a": 1}


@pytest.mark.parametrize("ser", SERIALIZERS)
@pytest.mark.parametrize(
    "payload",
    [
        None,
        True,
        1,
        1.5,
        "hello",
        [1, "x", None],
        {"nested": {"k": [1, 2]}},
    ],
)
def test_roundtrip_json_native_values(ser, payload):

    encoded = ser.dumps(payload)

    assert ser.loads(encoded) == payload
    assert ser.loads(encoded.decode("utf-8")) == payload


@pytest.mark.parametrize("ser", SERIALIZERS)
def test_dumps_decimal_with_builtin_default(ser):

    encoded = ser.dumps({"amount": Decimal("1.25")})

    assert ser.loads(encoded) == {"amount": "1.25"}


@pytest.mark.parametrize("ser", SERIALIZERS)
def test_unsupported_type_without_usable_default_raises(ser):

    with pytest.raises(TypeError):
        ser.dumps(object())


def test_json_serializer_encodes_datetime_and_date_via_default():

    payload = {
        "created_at": datetime(2026, 10, 18, 10, 0, 0),
        "day": date(2026, 10, 18),
    }

    assert json_ser.loads(json_ser.dumps(payload)) == {
        "created_at": "2026-10-18 10:00:00",
        "day": "2026-10-18",
    }


def test_orjson_serializer_natively_encodes_datetime_and_date():

    payload = {
        "created_at": datetime(2026, 10, 18, 10, 0, 0),
        "day": date(2026, 10, 18),
    }

    assert orjson_ser.loads(orjson_ser.dumps(payload)) == {
        "created_at": "2026-10-18T10:00:00",
        "day": "2026-10-18",
    }
