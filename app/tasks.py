"""Celery 异步任务流（阶段四 4.1，阶段五联调对齐版）。

- async_check_keyword_task(search_task_id)：执行一条已存在的 SearchTasks 子任务。
- submit_keyword_checks(keyword_id, task_ids=None, model_names=None)：把预创建的
  SearchTasks 推入 Redis 队列并行消费（阶段五 /keywords/submit 的主路径）。

任务内部：更新 SearchTasks 状态为 RUNNING -> 按 model_name 调度 API Client / Playwright
提取器拿到 LLMResponse -> 调用评分引擎 -> 持久化 GEOResults -> 状态置 SUCCESS；
异常则 FAILED + 失败原因 + 错误日志。

生命周期约定（与 API 层对齐）：
  API 层负责「创建 Keywords + SearchTasks(PENDING)」并拿到 task_ids；
  Worker 层只负责「把已存在的 SearchTasks 从 RUNNING 跑到 SUCCESS/FAILED」。
"""
from __future__ import annotations

import asyncio
import datetime as dt
import logging
from typing import List, Optional

from sqlmodel import Session

from app.celery_app import celery_app
from app.core.scoring import calculate_geo_score
from app.db.engine import engine
from app.models.db import GEOResults, Keywords, SearchTasks, TaskStatus
from app.models.schemas import LLMResponse

logger = logging.getLogger(__name__)

# 模型名 -> 通道分类
API_MODELS = {"openai", "deepseek", "ernie"}
BROWSER_MODELS = {"perplexity", "metaso"}
ALL_MODELS = sorted(API_MODELS | BROWSER_MODELS)


def _build_prompt(keyword: Keywords) -> str:
    """构造查询提示词（可按品牌策略调整）。"""
    return f"请介绍关于「{keyword.keyword}」的相关信息，并列出你参考的权威来源链接。"


async def _dispatch(model_name: str, prompt: str) -> LLMResponse:
    """按 model_name 调度 API Client 或 Playwright 提取器。"""
    if model_name in API_MODELS:
        from app.llm.factory import build_clients

        clients = await build_clients(enabled=[model_name])
        if not clients:
            raise RuntimeError(f"未配置 {model_name} 的 API Key，无法执行直连通道")
        client = clients[0]
        try:
            return await client.call_llm(prompt=prompt, enable_web_search=True)
        finally:
            await client.close()

    if model_name in BROWSER_MODELS:
        from app.browser.extractor import WebSearchExtractor

        extractor = WebSearchExtractor(site=model_name)
        try:
            return await extractor.query(prompt)
        finally:
            await extractor.close()

    raise ValueError(f"未知 model_name: {model_name}（可选: {ALL_MODELS}）")


async def _run_check(search_task_id: int, celery_task_id: Optional[str] = None) -> dict:
    """执行一条已存在的 SearchTasks（在 asyncio.run 内运行）。"""
    with Session(engine) as session:
        task = session.get(SearchTasks, search_task_id)
        if task is None:
            raise ValueError(f"SearchTask id={search_task_id} 不存在")

        keyword = session.get(Keywords, task.keyword_id)
        if keyword is None:
            raise ValueError(f"Keyword id={task.keyword_id} 不存在")
        model_name = task.model_name

        # 1) 置 RUNNING
        task.status = TaskStatus.RUNNING
        task.celery_task_id = celery_task_id
        task.updated_at = dt.datetime.utcnow()
        session.commit()

        try:
            # 2) 调度获取 LLMResponse
            resp = await _dispatch(model_name, _build_prompt(keyword))
            if resp.error:
                raise RuntimeError(f"通道返回错误: {resp.error}")

            # 3) 评分引擎
            score = calculate_geo_score(resp, keyword.keyword, keyword.target_domains)

            # 4) 持久化 GEOResults
            result = GEOResults(
                task_id=search_task_id,
                keyword_id=keyword.id,
                model_name=model_name,
                provider=resp.provider,
                raw_text=resp.text,
                citations_json=[c.model_dump() for c in resp.citations],
                score_link=score.score_link,
                score_mention=score.score_mention,
                score_position=score.score_position,
                score_total=score.score_total,
                matched_domains=score.matched_domains,
            )
            session.add(result)

            # 5) 任务置 SUCCESS
            task.status = TaskStatus.SUCCESS
            task.updated_at = dt.datetime.utcnow()
            session.commit()

            return {
                "task_id": search_task_id,
                "model": model_name,
                "score_total": score.score_total,
            }
        except Exception as exc:
            # 失败：记录 FAILED + 失败原因 + 错误日志（结果未入库，无需回滚）
            task.status = TaskStatus.FAILED
            task.error_message = str(exc)
            task.updated_at = dt.datetime.utcnow()
            session.commit()
            logger.exception(
                "async_check_keyword_task failed | search_task_id=%s model=%s",
                search_task_id, model_name,
            )
            return {"task_id": search_task_id, "model": model_name, "error": str(exc)}


@celery_app.task(name="async_check_keyword_task", bind=True)
def async_check_keyword_task(self, search_task_id: int) -> dict:
    """Celery 入口（同步包装，内部用 asyncio.run 跑异步流程）。"""
    return asyncio.run(_run_check(search_task_id, celery_task_id=self.request.id))


def submit_keyword_checks(
    keyword_id: Optional[int] = None,
    task_ids: Optional[List[int]] = None,
    model_names: Optional[List[str]] = None,
) -> List[int]:
    """批量分发：把 SearchTasks 推入 Redis 队列。

    两种用法：
    - 传入 task_ids：直接派发这些已存在的任务（阶段五 /keywords/submit 的主路径）。
    - 仅传 keyword_id（或 model_names）：本函数代为新建 SearchTasks 后再派发（兼容旧调用）。

    返回 search_task_id 列表。
    """
    if task_ids:
        for tid in task_ids:
            async_check_keyword_task.delay(tid)
        return task_ids

    if keyword_id is None:
        raise ValueError("submit_keyword_checks 需要 task_ids 或 keyword_id")

    models = model_names or list(ALL_MODELS)
    created: List[int] = []
    with Session(engine) as session:
        for m in models:
            t = SearchTasks(keyword_id=keyword_id, model_name=m, status=TaskStatus.PENDING)
            session.add(t)
            session.flush()
            created.append(t.id)
        session.commit()
    for tid in created:
        async_check_keyword_task.delay(tid)
    return created
