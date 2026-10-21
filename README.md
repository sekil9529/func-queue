# queue-func

**把 async 协程当成队列里的任务来投递与消费**——在进程内用内存队列跑通整条链路，并为 Redis、RabbitMQ、Kafka 等后端预留同一套 Broker / Producer / Consumer 抽象。

> 仅支持 **`async def` 协程函数**，不支持普通同步函数。

## 是什么

queue-func 做三件事：

1. **打包**：把「调用哪个协程、传什么 `(args, kwargs)`」编码成消息（可选 JSON / orjson 序列化）。
2. **投递**：Producer 写入通道（当前实现为 `asyncio.Queue`）。
3. **消费**：Consumer 拉取消息，经线程池限并发地 `await` 你的协程。

**Broker** 只在启动时装配共享的 `Message`、队列和 Producer/Consumer；运行期的 `publish` / `consume` **不经过** Broker 对象，避免变成「万事从中转」的大中介。

## 快速开始

依赖 Python 3.12+。安装（本地开发示例）：

```bash
poetry install
```

### 装饰器（推荐入门）

```python
import asyncio

from queue_func.factory import Backend, queue


@queue(
    Backend.QUEUE,
    enable_message_serializer=False,
    consume_timeout=0.5,
    maxsize=1000,
    consumer_pool_maxsize=10,
)
async def process_order(order_id: int, *, priority: str = "normal"):
    # 你的业务协程
    ...


async def main():
    await process_order.broker.start_consumer()
    await process_order.push(args=(42,), kwargs={"priority": "high"})
    # 收尾：await process_order.broker.stop_consumer(); await process_order.broker.join_consumer()


asyncio.run(main())
```

- `push` → 内部 `broker.publish(coro_args=..., coro_kwargs=...)`
- 消费侧使用 `broker.start_consumer()` / `stop_consumer()` / `join_consumer()`
- 仍可直接 `await process_order(1, priority="low")` 做本地调用

### 直接使用 Broker

需要更细控制时，自行组装 `Config` 与 `Broker`：

```python
from queue_func.broker.queue import Broker
from queue_func.config.queue import Config

async def work(x: int):
    ...

config = Config(work, maxsize=200, enable_message_serializer=True)
broker = Broker(config)

await broker.start_consumer()
await broker.publish((1,), {})
```

## 配置概览

| 区域 | 常见字段 | 作用 |
|------|----------|------|
| consumer | `coro`, `enable_consumer`, `consume_timeout`, `consumer_pool_maxsize` | 是否消费、拉取超时、协程并发上限 |
| broker / message | `message_cls`, `enable_message_serializer`, `maxsize`（队列后端） | 编解码、队列容量 |
| producer | `publish_timeout` | 队列满时 `put` 超时 |

完整字段见 `queue_func/config/general.py` 与 `queue_func/config/queue.py`。

## 适用场景

下面这些是 **当前内存队列版本** 就适合或已经开始有价值的用法；标注 **规划中** 的表示架构已预留、后端尚未实现。

### 1. 同进程内「异步解耦 + 控并发」

Web 或 RPC 的 handler 里只做校验与 `push`，单独 `consume` 在后台跑重逻辑（写库、调外部 API、算报表）。用 `consumer_pool_maxsize` 限制同时执行的协程数，避免把事件循环或下游打满。

**适合**：单体 async 服务、FastAPI/Starlette 同进程后台任务、需要 **背压**（`maxsize` + 可选 `publish_timeout`）时。

### 2. 统一「任务入口」、方便以后换传输层

业务只依赖 `publish((args,), {kwargs})` 和固定的 `async def` handler；序列化打开后，消息已是 bytes，将来换 Redis / Rabbit / Kafka 时，业务协程签名可不变，只换 Broker 实现与 Config。

**适合**：现在先单机跑通，但 **确定要上 MQ** 的项目；想先写好 consumer 侧逻辑再基础设施跟进。

### 3. 可测试的异步流水线

Producer、Consumer、Message 可单测；Broker 做集成测。装饰器 `queue` 适合在测试里 `push` 固定参数、断言协程副作用。

**适合**：重视 pytest、想把「投递」和「执行」分开测的团队。

### 4. 多生产者、单消费者（同一事件循环）

多个 coroutine 共用一个 `Broker` 的 `producer`，一个 `consumer` 循环 + 池化执行。本质是 **单进程 fan-in**，不是分布式队列。

**适合**：同一 asyncio 应用内多路写入、单 worker 顺序/池化处理的模型。

### 5. 与「重型 asyncio 队列库」的边界

queue-func **不是**通用分布式任务平台（对比 Celery、arq、Taskiq 的全套 worker 部署、调度、结果后端）。它更轻：**显式 Broker 装配 + 协程参数作为消息体 + 可扩展后端**。

**适合**：你要 **小核心、自己握配置和生命周期**；不需要开箱即用的集群调度。

### 6. 规划中：跨进程 / 跨服务（Redis、RabbitMQ、Kafka）

同一套 `Backend` 枚举与 Broker 扩展点，目标是把 `push` / `consume` 落到真实中间件。**当前仅 `Backend.QUEUE`（内存）可用。**

**适合（将来）**：多实例 worker、与现有 MQ 运维体系对接、需要持久化与重试策略（需在后续版本自行或库内扩展）。

## 不适用或需慎用的场景

- **同步 `def` 任务**：请包一层 `async def` 或改用其他任务库。
- **强一致分布式事务、复杂路由、延迟队列**：当前未提供；应用层或后续 Broker 再补。
- **CPU 密集型**：协程仍在 asyncio 里调度；CPU 应用应配合进程池或专用 worker，而不是默认 `PoolExecutor` 跑满 CPU 计算。
- **无界堆积且不限流**：请设置 `maxsize` / `publish_timeout` / 池大小，否则可能内存涨或拖垮下游。

## 项目结构（简要）

```
queue_func/
  broker/      # 通道装配（queue 等）
  producer/    # publish → 通道
  consumer/    # 从通道取消息 → 执行 coro
  message/     # pack / unpack
  config/      # pydantic dataclass 配置
  factory/     # Backend、queue 装饰器、QueueFunc / QueueFuncRuntime
  pool_executor/
  serializer/
```

## 开发与测试

```bash
conda activate queue-func   # 或你的 venv
pytest tests/ -q
```

## 许可证

Apache-2.0
