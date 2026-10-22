# coding: utf-8
"""
链式 QueueFunc：a 消费后 push 到 b，b 消费后 push 到 c，c 负责最终输出。

    main ──push──► [队列 a] ──► task_a ──push──► [队列 b] ──► task_b ──push──► [队列 c] ──► task_c ──► print

运行（项目根目录）:
    poetry run python examples/demo_queue.py
"""

import asyncio

from queue_func.factory import Backend, QueueFuncRuntime, queue

_Q = dict(
    backend=Backend.QUEUE,
    consume_timeout=0.15,
    maxsize=100,
    consumer_pool_maxsize=4,
)

_c_finished: list[str] = []
_T0: float = 0.0

_DELAY_A = 0.8
_DELAY_B = 0.8
_DELAY_C = 0.8
_DELAY_BETWEEN_PUSH = 1.2

_BAR = "─" * 58


def _elapsed() -> str:
    loop = asyncio.get_running_loop()
    return f"{loop.time() - _T0:7.2f}s"


def _log(stage: str, job: str, action: str) -> None:
    print(f"  {_elapsed()}  {stage:<5}  job={job:<10}  {action}", flush=True)


def _banner(title: str) -> None:
    print(f"\n{_BAR}\n  {title}\n{_BAR}", flush=True)


@queue(**_Q)
async def task_a(job: str) -> None:
    _log("A", job, f"consumer 出队 │ 开始处理 ({_DELAY_A}s)")
    await asyncio.sleep(_DELAY_A)
    _log("A", job, "处理完成 │ push ──► 队列 task_b")
    await task_b.push(args=(job,))


@queue(**_Q)
async def task_b(job: str) -> None:
    _log("B", job, f"consumer 出队 │ 开始处理 ({_DELAY_B}s)")
    await asyncio.sleep(_DELAY_B)
    _log("B", job, "处理完成 │ push ──► 队列 task_c")
    await task_c.push(args=(job,))


@queue(**_Q)
async def task_c(job: str) -> None:
    _log("C", job, f"consumer 出队 │ 开始处理 ({_DELAY_C}s)")
    await asyncio.sleep(_DELAY_C)
    _log("C", job, "★ 链路终点 │ 业务输出（此处 print）")
    print(f"           └─►  RESULT: {job!r}", flush=True)
    _c_finished.append(job)


async def wait_until(predicate, *, timeout: float = 30.0, interval: float = 0.05) -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if predicate():
            return
        await asyncio.sleep(interval)
    raise TimeoutError("等待链式任务完成超时")


async def main() -> None:
    global _T0
    _T0 = asyncio.get_running_loop().time()

    print(_BAR)
    print("  链式 QueueFunc 演示")
    print("  流程: MAIN ──push──► A ──push──► B ──push──► C ──输出")
    print("  日志: 时间 │ 阶段 │ job │ 动作")
    print(_BAR)

    runtime = QueueFuncRuntime([task_a, task_b, task_c])
    await runtime.start()
    _log("MAIN", "-", "QueueFuncRuntime.start() │ consumer 启动顺序: C → B → A")

    jobs = ["订单-001", "订单-002"]
    for i, job in enumerate(jobs):
        if i:
            _banner(f"间隔 {_DELAY_BETWEEN_PUSH}s 后投递下一条")
            await asyncio.sleep(_DELAY_BETWEEN_PUSH)
        _banner(f"第 {i + 1} 条 │ MAIN push ──► 队列 task_a")
        _log("MAIN", job, "publish │ push ──► 队列 task_a")
        await task_a.push(args=(job,))

    _banner("等待整条链路跑完（以 C 输出为准）")
    await wait_until(lambda: len(_c_finished) >= len(jobs))

    _banner("汇总")
    for j in jobs:
        mark = "OK" if j in _c_finished else "MISSING"
        _log("MAIN", j, f"状态 {mark}")
    _log("MAIN", "-", "QueueFuncRuntime.stop()")
    await runtime.stop()
    print(f"\n{_BAR}\n  演示结束\n{_BAR}\n", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
