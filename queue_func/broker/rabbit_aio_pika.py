# coding: utf-8

import typing as t

from queue_func.broker.base import BaseBroker as _BaseBroker
from queue_func.consumer.rabbit_aio_pika import Consumer
from queue_func.producer.rabbit_aio_pika import Producer
from queue_func.shared_resource.rabbit_aio_pika import Resource

if t.TYPE_CHECKING:
    from queue_func.config.rabbit_aio_pika import Config


class Broker(_BaseBroker["Config", bytes]):
    """RabbitMQ 通道。一条连接上分开发布和消费，再交给 Producer 和 Consumer。"""

    def __init__(self, config: "Config"):

        resource = Resource(
            serializer_cls=config.serializer_cls,
            url=config.url,
            queue_name=config.queue_name,
            enable_declare_queue=config.enable_declare_queue,
            queue_durable=config.queue_durable,
            queue_exclusive=config.queue_exclusive,
            queue_passive=config.queue_passive,
            queue_auto_delete=config.queue_auto_delete,
            queue_arguments=config.queue_arguments,
        )
        self._producer = Producer(
            resource=resource,
            publish_timeout=config.publish_timeout,
            exchange_name=config.exchange_name,
            routing_key=config.routing_key,
            delivery_mode=config.delivery_mode,
        )
        self._consumer = Consumer(
            resource=resource,
            prefetch_count=config.prefetch_count,
            prefetch_size=config.prefetch_size,
            global_qos=config.global_qos,
            coro=config.coro,
            enable_consumer=config.enable_consumer,
            consume_timeout=config.consume_timeout,
            pool_executor_cls=config.consumer_pool_executor_cls,
            pool_maxsize=config.consumer_pool_maxsize,
        )
