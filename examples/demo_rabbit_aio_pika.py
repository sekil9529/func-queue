# coding: utf-8
"""RabbitMQ 链式队列：a 消费后 push 到 b。

需要本机 RabbitMQ，账号 guest/guest，端口 5672。
队列不存在时会创建。

运行（项目根目录）:
    poetry run python examples/demo_rabbit_aio_pika.py
"""

import asyncio

from queue_func.factory import Backend, QueueFuncRuntime, queue


@queue(
    Backend.RABBIT_AIO_PIKA,
    url="amqp://guest:guest@127.0.0.1:5672/",
    queue_name="demo_rabbit_b",
    enable_declare_queue=True,
    queue_durable=True,
    consume_timeout=0.5,
)
async def task_b(order_id: str) -> None:

    print("b", order_id)


@queue(
    Backend.RABBIT_AIO_PIKA,
    url="amqp://guest:guest@127.0.0.1:5672/",
    queue_name="demo_rabbit_a",
    enable_declare_queue=True,
    queue_durable=True,
    consume_timeout=0.5,
)
async def task_a(order_id: str) -> None:

    print("a", order_id)
    await task_b.push(args=(order_id,))


async def main() -> None:

    runtime = QueueFuncRuntime([task_a, task_b])
    await runtime.start()
    await task_a.push(args=("订单-001",))
    await runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
