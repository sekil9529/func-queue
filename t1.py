# coding: utf-8

import inspect
import typing as t
from typing import List, Dict, get_type_hints

from t2 import A


def example_function(param1: int, param2: 'str', /, *, param3: List[int], param4: 'Dict[str, int]', param5: "list[dict[str, t.Any]]", a: "A") -> None:
    pass


def get_actual_type(type_hint):
    """获取类型提示的实际类型"""
    if hasattr(type_hint, '__origin__'):
        return type_hint.__origin__
    return type_hint


def get_function_param_types(func):
    # 获取函数签名
    sig = inspect.signature(func)
    # 获取类型提示（包括引号包裹的类型）
    type_hints = get_type_hints(func)

    params = []
    for name, param in sig.parameters.items():
        print(name, param.annotation)
        param_type = type_hints.get(name, param.annotation)
        param_info = {
            "name": name,
            "kind": param.kind,
            "type_hint": param_type,
            "actual_type": get_actual_type(param_type),
        }
        params.append(param_info)

    return params


if __name__ == '__main__':

    for item in get_function_param_types(example_function):
        print(item)
