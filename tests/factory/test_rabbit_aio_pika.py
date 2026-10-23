# coding: utf-8

from queue_func.factory import Backend, queue

from tests.helpers import run_async
from tests.rabbit_aio_pika_fakes import FakeWorld, patch_connect, wait_until


@run_async
async def test_queue_decorator_publishes_to_rabbit_consumer():

    received: list[int] = []

    @queue(
        Backend.RABBIT_AIO_PIKA,
        url="amqp://guest:guest@127.0.0.1/",
        queue_name="jobs",
        consume_timeout=0.05,
        consumer_pool_maxsize=2,
    )
    async def work(n: int):
        received.append(n)

    world = FakeWorld()

    with patch_connect(world):
        await work.broker.start_consumer()
        await work.push(args=(9,))
        await wait_until(lambda: received == [9])

        world.queue.force_timeout = True
        await work.broker.stop_consumer()
        world.queue.event.set()
        await work.broker.join_consumer()
        await work.broker.stop_producer()
        await work.broker.join_producer()

    assert received == [9]
    assert world.connection.closed is True
