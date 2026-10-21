# coding: utf-8

import asyncio
import functools


def run_async(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper
