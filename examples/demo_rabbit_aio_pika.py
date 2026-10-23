# coding: utf-8
"""
RabbitMQ 上的链式 QueueFunc：a 消费后 push 到 b，b 负责输出。

    main ──每 3 秒 20 条──► [队列 a] ──► task_a ──push──► [队列 b] ──► task_b ──► print

投递持续 12 秒。默认交换机，routing key 使用队列名。
enable_declare_queue=True 时，队列不存在会创建。

运行（项目根目录，RabbitMQ 在 127.0.0.1:5672，guest/guest）:
    poetry run python examples/demo_rabbit_aio_pika.py
"""

import asyncio
import random
from datetime import datetime

import orjson

from queue_func.factory import Backend, QueueFuncRuntime, queue

_BATCH_SIZE = 200
_BATCH_INTERVAL = 1.0
_RUN_SECONDS = 10.0
_SKUS = ("键盘", "鼠标", "显示器", "耳机", "硬盘")
_COLORS = ("黑", "白", "银", "灰")
_CHANNELS = ("app", "web", "mini_program", "store")
_PROVINCES = ("浙江", "江苏", "广东", "上海", "北京")
_LINE_COUNT = 160
_TIMELINE_COUNT = 40

_finished: list[str] = []
_expected = 0


def _now() -> str:

    return datetime.now().isoformat(sep=" ")


def _random_order() -> dict:

    order_id = f"ORD-{random.randint(100000, 999999)}"
    items = []
    for line in range(1, _LINE_COUNT + 1):
        price = round(random.uniform(19, 899), 2)
        qty = random.randint(1, 5)
        items.append({
            "line": line,
            "sku": f"SKU-{random.randint(10000, 99999)}",
            "name": random.choice(_SKUS),
            "qty": qty,
            "price": price,
            "amount": round(price * qty, 2),
            "warehouse": {
                "code": f"WH-{random.randint(1, 9)}",
                "zone": random.choice(("A", "B", "C")),
                "bin": f"{random.randint(1, 40):02d}-{random.randint(1, 20):02d}",
            },
            "attrs": {
                "color": random.choice(_COLORS),
                "spec": random.choice(("标准", "套装", "旗舰")),
            },
        })
    amount = round(sum(item["amount"] for item in items), 2)
    province = random.choice(_PROVINCES)
    return {
        "order_id": order_id,
        "status": "paid",
        "channel": random.choice(_CHANNELS),
        "created_at": _now(),
        "buyer": {
            "id": f"U{random.randint(100000, 999999)}",
            "name": f"用户{random.randint(1, 9999)}",
            "phone": f"1{random.randint(3000000000, 9999999999)}",
            "level": random.choice(("normal", "silver", "gold")),
            "tags": random.sample(("new", "vip", "return", "coupon"), k=2),
        },
        "address": {
            "province": province,
            "city": province,
            "district": "西湖区",
            "detail": f"文三路 {random.randint(1, 800)} 号",
            "receiver": f"收件人{random.randint(1, 999)}",
            "phone": f"1{random.randint(3000000000, 9999999999)}",
        },
        "items": items,
        "payment": {
            "method": random.choice(("alipay", "wechat", "card")),
            "trade_no": f"T{random.randint(10**11, 10**12 - 1)}",
            "currency": "CNY",
            "amount": amount,
            "paid": True,
        },
        "invoice": {
            "required": True,
            "title": f"公司{random.randint(1, 200)}",
            "tax_no": f"91330000{random.randint(10**9, 10**10 - 1)}",
        },
        "timeline": [
            {
                "at": _now(),
                "action": random.choice(("created", "paid", "allocated", "packed")),
                "operator": f"op-{random.randint(1, 50)}",
                "note": f"第 {index} 步处理",
            }
            for index in range(1, _TIMELINE_COUNT + 1)
        ],
    }


@queue(
    Backend.RABBIT_AIO_PIKA,
    url="amqp://guest:guest@127.0.0.1:5672/?heartbeat=100",
    queue_name="demo_rabbit_b",
    enable_declare_queue=True,
    queue_durable=True,
    consume_timeout=0.5,
    prefetch_count=20,
    consumer_pool_maxsize=500,
    # enable_consumer=False,
)
async def task_b(seq: int, published_at: str, order: dict) -> None:

    consumed_at = datetime.now()
    lag = (consumed_at - datetime.fromisoformat(published_at)).total_seconds()
    body_bytes = len(orjson.dumps(order))
    print(
        f"  B 消费 | {lag:.4f}s | 序号 {seq} | 消费 {consumed_at.isoformat(sep=' ')} | 投递 {published_at} | {order['order_id']} | {len(order['items'])} 行 | {body_bytes}B",
        flush=True,
    )
    _finished.append(order["order_id"])


@queue(
    Backend.RABBIT_AIO_PIKA,
    url="amqp://guest:guest@127.0.0.1:5672/?heartbeat=100",
    queue_name="demo_rabbit_a",
    exchange_name="amq.direct",
    routing_key="aaa",
    enable_declare_queue=True,
    queue_durable=True,
    consume_timeout=0.5,
    prefetch_count=20,
    consumer_pool_maxsize=200,
)
async def task_a(seq: int, _published_at: str, order: dict) -> None:

    await task_b.push(args=(seq, _now(), order))


async def _wait_until(predicate, *, timeout: float = 180.0, interval: float = 0.05) -> None:

    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if predicate():
            return
        await asyncio.sleep(interval)
    raise TimeoutError(f"等待 RabbitMQ 消费完成超时 | 已完成 {len(_finished)}/{_expected}")


async def _publish_for(seconds: float) -> int:

    loop = asyncio.get_running_loop()
    deadline = loop.time() + seconds
    total = 0
    batch = 0
    while True:
        batch += 1
        elapsed = seconds - (deadline - loop.time())
        print(
            f"MAIN 第 {batch} 批 | 已运行 {elapsed:.1f}s | 投递 {_BATCH_SIZE} 条 -> demo_rabbit_a",
            flush=True,
        )
        for order in (_random_order() for _ in range(_BATCH_SIZE)):
            total += 1
            published_at = _now()
            print(f"MAIN 投递 | 序号 {total} | 投递 {published_at} | {order['order_id']}", flush=True)
            await task_a.push(args=(total, published_at, order))
        if loop.time() >= deadline:
            break
        pause = min(_BATCH_INTERVAL, deadline - loop.time())
        print(f"MAIN 等待 {pause:.1f}s 后投递下一批", flush=True)
        await asyncio.sleep(pause)
    return total


async def main() -> None:

    global _expected
    runtime = QueueFuncRuntime([task_a, task_b])
    await runtime.start()
    print(
        f"consumer 已启动 | 顺序: B -> A | 每 {_BATCH_INTERVAL:.0f}s 投递 {_BATCH_SIZE} 条 | 持续 {_RUN_SECONDS:.0f}s",
        flush=True,
    )

    _expected = await _publish_for(_RUN_SECONDS)
    print(f"投递结束 | 共 {_expected} 条 | 等待消费完成", flush=True)
    await _wait_until(lambda: len(_finished) >= _expected)
    print(f"完成 | {len(_finished)}/{_expected}", flush=True)
    await runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
