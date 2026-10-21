# queue-func

**把 async 协程当成队列里的任务来投递与消费**——进程内用内存队列跑通链路，并为 RabbitMQ、Kafka 等后端预留同一套 Broker / Producer / Consumer 抽象。

> 仅支持 **`async def`**，不支持普通同步函数。需要 **Python 3.12+**。

## 关键概念

1. **`@queue`**：把协程包成 `QueueFunc`，提供 `push(args=..., kwargs=...)` 与 `broker`。
2. **消息**：`(args, kwargs)` 经 `Message` 打包；可选 JSON / orjson 序列化。
3. **消费**：Consumer 从通道取消息，经池化 `await` 你的协程（`consumer_pool_maxsize` 限并发）。

运行期的 `publish` / `consume` 在 Producer / Consumer 内完成；Broker 主要负责装配与生命周期，不做「万事中转」。

## 快速开始

```bash
poetry install
```

单个任务：

```python
import asyncio

from queue_func.factory import Backend, queue


@queue(Backend.QUEUE, enable_message_serializer=False, consume_timeout=0.5, maxsize=1000)
async def process_order(order_id: int):
    ...


async def main():
    await process_order.broker.start_consumer()
    await process_order.push(args=(42,))
    await process_order.broker.stop_consumer()
    await process_order.broker.join_consumer()


asyncio.run(main())
```

- `push` → `broker.publish(coro_args=..., coro_kwargs=...)`
- 仍可直接 `await process_order(1)` 做本地调用（不经队列）

多个 `QueueFunc`（各自独立队列）用 **`QueueFuncRuntime`** 统一启停；`start()` 按注册列表**反序**启动 consumer（下游先就绪，便于链式 `push`）：

```python
from queue_func.factory import Backend, QueueFuncRuntime, queue

# task_a 内 await task_b.push(...)，task_b 内 await task_c.push(...) 等


async def main():
    runtime = QueueFuncRuntime([task_a, task_b, task_c])
    await runtime.start()
    await task_a.push(args=("job-1",))
    await runtime.stop()
```

可运行示例（a → b → c 链式投递 + 控制台日志）：

```bash
poetry run python examples/demo_queue.py
```

需要自行组装通道时，使用 `Config` + `queue_func.broker.queue.Broker`（见 `queue_func/config/`）。

## 使用场景

| 场景 | 说明 |
|------|------|
| 同进程解耦 + 控并发 | Handler 里 `push`，后台 consumer 跑重逻辑；`maxsize` / `publish_timeout` 做背压 |
| 多段流水线 | 多个 `QueueFunc`，在协程里继续 `push` 到下一环；用 `QueueFuncRuntime` 管生命周期 |
| 先单机、后换 MQ | 打开序列化后消息已是 bytes，后续可换 Broker 实现，协程签名尽量不变 |
| 可测 | Producer / Consumer / `push` 副作用分开测；`tests/` 有集成示例 |

**规划中**：`Backend` 除内存队列外的 RabbitMQ / Kafka（**当前仅 `Backend.QUEUE` 可用**）。

**不太适合**：同步任务、分布式调度/结果后端/Celery 级平台、无界堆积不限流、纯 CPU 密集（应另配进程池或 worker）。

## 项目结构

```
queue_func/
  broker/ producer/ consumer/ message/ config/
  factory/          # Backend、queue、QueueFunc、QueueFuncRuntime
  pool_executor/ serializer/
examples/demo_queue.py
```

## 开发与测试

```bash
pytest tests/ -q
```

## 许可证

Apache-2.0
