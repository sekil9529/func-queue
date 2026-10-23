# queue-func

把 **`async def` 协程** 变成可 **`push`** 的队列任务：在 asyncio 里投递、消费，并按通道控制并发与背压。

仓库：[github.com/sekil9529/queue-func](https://github.com/sekil9529/queue-func)。版本记录见 [Changelog.rst](Changelog.rst)。

> **需要 Python 3.12 及以上。** 任务入口必须是协程函数，普通函数不能作为任务。
>
> RabbitMQ 后端需要另装可选依赖，底层使用 [aio-pika](https://github.com/mosquito/aio-pika) `^9.6`。

## 特点

- 完全在 asyncio 里运行。消费者在同一事件循环里按上限并发执行任务，可以和 FastAPI / Starlette 放在一个进程里。
- 一条链路是序列化、投递、反序列化、执行。启停由通道或 `QueueFuncRuntime` 显式管理。
- 每个 `QueueFunc` 有自己的队列和消费并发上限。`QueueFuncRuntime` 可以同时跑多段流水线，各段互不影响。
- 序列化器的 `pack` / `unpack` 决定队列里的数据结构。
- 通过 `register_backend` 接入新的队列后端。

## 当前后端

| 后端 | 说明 |
|------|------|
| `Backend.QUEUE` | 进程内 `asyncio.Queue` |
| `Backend.RABBIT_AIO_PIKA` | RabbitMQ，安装可选依赖 `rabbit` |

内存队列的消息留在进程里，序列化默认是 `raw`（队列中仍是 `(args, kwargs)`）。RabbitMQ 默认用 orjson，队列中是 `bytes`。

## 安装

```shell
pip install queue-func
```

使用 RabbitMQ：

```shell
pip install "queue-func[rabbit]"
```

从仓库安装（开发）：

```shell
git clone https://github.com/sekil9529/queue-func.git
cd queue-func
poetry install -E rabbit
```

## 用法

### 进程内队列

```python
import asyncio

from queue_func.factory import Backend, queue


@queue(Backend.QUEUE, consume_timeout=0.5, maxsize=1000)
async def process_order(order_id: int) -> None:
    print(order_id)


async def main() -> None:
    await process_order.broker.start_consumer()
    await process_order.push(args=(42,))
    await process_order.broker.stop_consumer()
    await process_order.broker.join_consumer()


asyncio.run(main())
```

`push` 就是 `broker.publish`。不传 `timeout` 时用配置里的 `publish_timeout`；传入数字只作用于这一次。`None` 表示不限时。超时抛出 `queue_func.PublishTimeoutError`。

装饰之后仍可直接调用，不经过队列：

```python
await process_order(1)
```

### 多段流水线

`QueueFuncRuntime.start()` 按列表反序启动消费者，下游先就绪。`stop()` 先逐个停止消费者，再停止全部生产者。

```python
import asyncio

from queue_func.factory import Backend, QueueFuncRuntime, queue


@queue(Backend.QUEUE, consumer_pool_maxsize=4)
async def task_b(job: str) -> None:
    print(job)


@queue(Backend.QUEUE, consumer_pool_maxsize=2)
async def task_a(job: str) -> None:
    await task_b.push(args=(job,))


async def main() -> None:
    runtime = QueueFuncRuntime([task_a, task_b])
    await runtime.start()
    await task_a.push(args=("job-1",))
    await runtime.stop()


asyncio.run(main())
```

三段链式示例（含日志）：

```shell
poetry run python examples/demo_queue.py
```

### RabbitMQ

`url` 和 `queue_name` 必填。`enable_declare_queue=True` 时，队列不存在会创建。默认交换机名是 `""`，路由键默认用队列名。`push` 会等待发布确认；`publish_timeout` 是这次确认的超时。

消息交给消费池之后就确认。处理函数出错不会把消息退回队列。`stop` 会设上停止标志，当前这次拉取结束（空闲时最多再等一个 `consume_timeout`）后退出；还没取走的消息留在 RabbitMQ 上。

同一个 `QueueFunc` 的生产者和消费者可以分进程运行。只投递的进程把 `enable_consumer` 设为 `False`。

```python
import asyncio

from queue_func.factory import Backend, queue


@queue(
    Backend.RABBIT_AIO_PIKA,
    url="amqp://guest:guest@127.0.0.1/",
    queue_name="process_order",
    enable_declare_queue=True,
)
async def process_order(order_id: int) -> None:
    print(order_id)


async def main() -> None:
    await process_order.broker.start_consumer()
    await process_order.push(args=(42,))
    await process_order.broker.stop_consumer()
    await process_order.broker.join_consumer()
    await process_order.broker.stop_producer()
    await process_order.broker.join_producer()


asyncio.run(main())
```

本地 RabbitMQ（`127.0.0.1:5672`，`guest` / `guest`）上的链式示例：

```shell
poetry run python examples/demo_rabbit_aio_pika.py
```

常用参数：

| 参数 | 作用 |
|------|------|
| `consumer_pool_maxsize` | 同时执行的协程数，默认 200 |
| `consume_timeout` | 一次拉取的等待时间，默认 2 秒 |
| `publish_timeout` | 投递等待上限，默认不限 |
| `maxsize` | 仅内存队列，`asyncio.Queue` 容量，默认 200 |
| `serializer_cls` | 队列中的数据结构 |
| `prefetch_count` | 仅 RabbitMQ，未确认消息窗口 |
| `delivery_mode` | 仅 RabbitMQ，默认持久化 |
| `exchange_name` / `routing_key` | 仅 RabbitMQ |

其余字段见 `queue_func.config.queue.Config` 和 `queue_func.config.rabbit_aio_pika.Config`。

## 架构

一个 `@queue` 装饰的协程就是一条队列。`push` 投到它自己这条队列上。

- **Broker** 组装生产者、消费者和双方共用的资源，并提供启停与投递。
- **Producer** 序列化后把数据写入队列。
- **Consumer** 取出数据，反序列化后交给消费池。
- **PoolExecutor** 按并发上限执行业务协程。

```mermaid
flowchart TB
  PUSH["投递"] --> B["通道"]
  B --> PRO["生产者"]
  B -.->|启停| CON["消费者"]

  PRO -->|序列化| Q[("队列")]
  Q -->|反序列化| CON
  CON --> POOL["消费池"]
  POOL --> FN["业务协程"]
```

## 项目结构

```
queue_func/
├── broker/
├── producer/
├── consumer/
├── serializer/       # raw、orjson
├── shared_resource/
├── config/
├── factory/          # @queue、QueueFunc、QueueFuncRuntime
├── pool_executor/
└── utils/
examples/
├── demo_queue.py
└── demo_rabbit_aio_pika.py
```

## 开发与测试

```shell
poetry install -E rabbit
pytest
```

`pytest.ini` 会生成覆盖率页面（`htmlcov/`）和 `report.html`。

## 版本

遵循[语义化版本](https://semver.org/lang/zh-CN/)。变更记录在 [Changelog.rst](Changelog.rst)。

## 许可证

Apache-2.0
