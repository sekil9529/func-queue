# coding: utf-8

"""Import builder modules so they register with :func:`register_backend`."""

from queue_func.backends.queue import build as queue
from queue_func.backends.rabbit_aio_pika import build as rabbit_aio_pika

__all__ = (
    "queue",
    "rabbit_aio_pika",
)
