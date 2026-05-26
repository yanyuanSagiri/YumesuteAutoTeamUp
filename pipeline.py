# pipeline.py
import asyncio
import queue
import json
import aiohttp
from typing import Any, Optional

# ================== 你的配件扩展逻辑 ==================
def processor_accessory(base_state: dict, accessory_list: list) -> list[dict]:
    """
    将一个基础团队状态扩展为多个完整团队（含 accessories）。
    base_state 示例:
        {
            "actors": [46, 1, 5, 29, 12],
            "posters": [141, 189, 107, 184, 183],
            "leader": 1        # 可选
        }
    accessory_list: 可用的配件ID列表（或其他所需数据）
    返回: 完整 team 字典列表，每个 team 都包含 "accessories" 字段
    """
    expanded = []
    # ------------------------------------------------
    # 这里填入你原来的 processor_accessory 实现
    # 示例：简单给每个 base_state 加上固定的配件组合
    # 实际逻辑请按你的需求替换
    for acc_combo in generate_accessory_combinations(accessory_list):
        team = base_state.copy()
        team["accessories"] = acc_combo   # 列表，长度为10
        expanded.append(team)
    # ------------------------------------------------
    return expanded


def generate_accessory_combinations(accessory_list):
    """临时示例：只返回一个固定组合，实际应返回所有可能的合法组合"""
    # 请替换为你的真实逻辑
    return [[accessory_list[i % len(accessory_list)] for i in range(10)]]


# ================== 异步请求与结果处理 ==================
async def _send_one_request(session, team: dict, api_url: str, data_file: str,
                            photo: list, sensenotation: int, score_only: bool):
    payload = {
        "data_file": data_file,
        "team": team,
        "photo": photo,
        "sensenotation": sensenotation,
        "score_only": score_only
    }
    try:
        async with session.post(api_url, json=payload) as resp:
            data = await resp.json()
            return {"team": team, "result": data}
    except Exception as e:
        return {"team": team, "error": str(e)}


async def _expansion_and_request_loop(
    sync_queue: queue.Queue,
    result_queue: asyncio.Queue,
    accessory_list: list,
    api_url: str,
    data_file: str,
    photo: list,
    sensenotation: int,
    score_only: bool = False,
    concurrency: int = 10
):
    """从同步队列取基础状态，扩展后并发请求，结果放入 result_queue"""
    semaphore = asyncio.Semaphore(concurrency)
    loop = asyncio.get_running_loop()

    async def _bounded_send(session, team):
        async with semaphore:
            return await _send_one_request(session, team, api_url, data_file,
                                           photo, sensenotation, score_only)

    async with aiohttp.ClientSession() as session:
        while True:
            # 用线程池从同步队列获取，避免阻塞事件循环
            base_state = await loop.run_in_executor(None, sync_queue.get)
            if base_state is None:          # 结束信号
                sync_queue.task_done()
                break

            # 扩展 accessories（如果是 CPU 密集也可放线程池）
            expanded_teams = await loop.run_in_executor(
                None, processor_accessory, base_state, accessory_list
            )

            # 并发发送所有扩展出的请求，并随着完成逐个推入结果队列
            tasks = [asyncio.create_task(_bounded_send(session, t)) for t in expanded_teams]
            for coro in asyncio.as_completed(tasks):
                res = await coro
                await result_queue.put(res)

            sync_queue.task_done()

    # 通知结果消费者结束
    await result_queue.put(None)


async def _result_saver_loop(result_queue: asyncio.Queue, save_func):
    """从结果队列取出结果并调用保存函数"""
    while True:
        item = await result_queue.get()
        if item is None:
            result_queue.task_done()
            break
        # 这里调用你自定义的保存逻辑，例如写入文件或数据库
        save_func(item)
        result_queue.task_done()


# ================== 启动流水线 ==================
def start_pipeline(
    accessory_list: list,
    api_url: str = "http://127.0.0.1:3456/calc",
    data_file: str = "example.json",
    photo: Optional[list] = None,
    sensenotation: int = 1146,
    score_only: bool = False,
    concurrency: int = 10,
    save_func = print   # 默认打印，你可以换成写文件等
):
    """
    启动整个异步流水线，返回：
        sync_queue:   供 automatic_formation 推送基础状态的队列
        tasks:        (expansion_task, saver_task) 异步任务，需要被事件循环管理
    """
    sync_queue = queue.Queue(maxsize=100)      # 有界队列，实现背压
    result_queue = asyncio.Queue()

    if photo is None:
        photo = [2,3,4,5,6]    # 默认值

    expansion_task = asyncio.create_task(
        _expansion_and_request_loop(
            sync_queue, result_queue, accessory_list, api_url,
            data_file, photo, sensenotation, score_only, concurrency
        )
    )
    saver_task = asyncio.create_task(_result_saver_loop(result_queue, save_func))

    return sync_queue, (expansion_task, saver_task)