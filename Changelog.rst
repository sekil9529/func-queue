.. _changelog:

================
 版本变更记录
================

本文档记录 **queue-func** 各版本的缺陷修复与新功能。


.. _version-unreleased:

未发布
======

（暂无）


.. _version-0.2.1:

0.2.1
=====

:release-date: 2026-10-23

功能
~~~~

- 新增 ``Backend.RABBIT_AIO_PIKA``：通过可选依赖 aio-pika（``^9.6``）接入 RabbitMQ。


.. _version-0.1.2:

0.1.2
=====

:release-date: 2026-10-22

功能
~~~~

- 合并 ``message`` 与 ``serializer``，并支持 orjson。
- 新增 ``push`` 超时控制（支持按次 ``timeout``，并与配置项 ``publish_timeout`` 在各 Backend 上行为一致）。超时抛出 ``PublishTimeoutError``。


.. _version-0.1.0:

0.1.0
=====

:release-date: 2026-10-21

功能
~~~~

- 新增 ``@queue`` 装饰器与 ``QueueFunc``，支持 ``push(args=..., kwargs=...)`` 及直接 ``await`` 调用。
- 新增进程内 ``Backend.QUEUE`` 通道：Producer、Consumer，以及显式的 ``start_consumer`` / ``stop_consumer`` / ``join`` 生命周期。
- 新增 ``Message`` 层，可对 ``(args, kwargs)`` 可选 JSON / orjson 序列化。
- 新增 ``QueueFuncRuntime``，按固定顺序批量启动、关闭多个 ``QueueFunc``。
- 新增基于池化的 consumer 并发上限（``consumer_pool_maxsize``）。
- 新增 ``register_backend`` 扩展点，便于后续接入 RabbitMQ、Kafka 等后端。

文档
~~~~

- 新增 README：快速开始、``QueueFuncRuntime``、使用场景。
- 新增 ``examples/demo_queue.py``：a → b → c 链式投递与控制台日志示例。

测试
~~~~

- 新增 pytest：broker、producer、consumer、serializer、装饰器与 runtime 等。

其它
~~~~

- 包名定为 **queue-func**，要求 Python 3.12+。
