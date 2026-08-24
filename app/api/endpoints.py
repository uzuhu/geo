"""阶段五核心交付接口（FastAPI 路由）。

三个接口：
1) POST /api/v1/keywords/submit         —— 提交关键词 + 目标域名 + 模型，创建任务并异步派发评测。
2) GET  /api/v1/tasks/{task_id}/status  —— 按 search_task_id 或 celery_task_id 查询单条/批量任务状态。
3) GET  /api/v1/reports/{keyword_id}    —— 聚合某关键词在各模型下的最新 GEO 报表。

注意：数据库操作为同步（SQLAlchemy/SQLModel），在 async 路由内直接以 Session 上下文执行，
适用于当前吞吐规模；后续若压测瓶颈明显可改为依赖注入 + 线程池。
"""
from __future__ import annotations

import datetime as dt
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.config import settings
from app.core.scoring import extract_domain
from app.db.engine import engine
from app.models.db import GEOResults, Keywords, SearchTasks, TaskStatus
from app.tasks import ALL_MODELS, submit_keyword_checks

router = APIRouter(tags=["geo"])


# ----------------------------- 阶段六：API 密钥鉴权 -----------------------------

async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """系统级鉴权依赖：校验请求头 X-API-Key 是否与 GEO_SYSTEM_AUTH_KEY 一致。

    不一致 / 缺失直接抛 401。若 GEO_SYSTEM_AUTH_KEY 未配置（空），强制拒绝一切请求，
    避免公网部署时因忘记设置密钥而裸奔。
    """
    expected = settings.GEO_SYSTEM_AUTH_KEY
    if not expected or x_api_key != expected:
        raise HTTPException(
            status_code=401,
            detail="缺少或非法的 X-API-Key 请求头",
            headers={"WWW-Authenticate": "X-API-Key"},
        )
    return x_api_key


# ----------------------------- 请求 / 响应模型 -----------------------------


class KeywordSubmitRequest(BaseModel):
    keywords: List[str] = Field(..., min_length=1, description="待监测的关键词/品牌词列表")
    target_domains: List[str] = Field(
        default_factory=list, description="绑定的目标域名，用于引文域名级匹配"
    )
    models: List[str] = Field(
        default_factory=list, description="检测模型列表；为空则使用全部模型"
    )
    monitor_frequency: str = Field(default="daily", description="监控频率：hourly/daily/weekly")


class SubmitResponse(BaseModel):
    keyword_ids: List[int]
    models: List[str]
    task_ids: List[int]
    message: str


class TaskStatusView(BaseModel):
    task_id: int
    keyword_id: int
    model_name: str
    status: str
    celery_task_id: Optional[str] = None
    error_message: Optional[str] = None
    score_total: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ----------------------------- 1) 提交评测任务 -----------------------------


@router.post(
    "/keywords/submit",
    response_model=SubmitResponse,
    status_code=201,
    dependencies=[Depends(verify_api_key)],
)
async def submit_keywords(req: KeywordSubmitRequest):
    models = req.models or list(ALL_MODELS)
    unknown = [m for m in models if m not in ALL_MODELS]
    if unknown:
        raise HTTPException(
            status_code=400, detail=f"未知模型: {unknown}（可选: {ALL_MODELS}）"
        )

    keyword_ids: List[int] = []
    task_ids: List[int] = []

    # 同步事务：创建 Keywords + 每个 (关键词 × 模型) 一条 SearchTasks(PENDING)
    with Session(engine) as session:
        for kw in req.keywords:
            keyword = Keywords(
                keyword=kw,
                target_domains=req.target_domains,
                monitor_frequency=req.monitor_frequency,
            )
            session.add(keyword)
            session.flush()  # 拿到 keyword.id
            keyword_ids.append(keyword.id)
            for m in models:
                task = SearchTasks(
                    keyword_id=keyword.id, model_name=m, status=TaskStatus.PENDING
                )
                session.add(task)
                session.flush()  # 拿到 task.id
                task_ids.append(task.id)
        session.commit()

    # 异步派发到 Celery（broker 不可达时回滚任务状态并 503）
    try:
        submit_keyword_checks(task_ids=task_ids)
    except Exception as exc:  # noqa: BLE001
        with Session(engine) as s2:
            for tid in task_ids:
                t = s2.get(SearchTasks, tid)
                if t and t.status == TaskStatus.PENDING:
                    t.status = TaskStatus.FAILED
                    t.error_message = f"任务派发失败（请确认 Redis/Celery 已启动）: {exc}"
                    t.updated_at = dt.datetime.utcnow()
            s2.commit()
        raise HTTPException(
            status_code=503,
            detail=f"任务派发失败，请确认 Redis/Celery 已启动: {exc}",
        )

    return SubmitResponse(
        keyword_ids=keyword_ids,
        models=models,
        task_ids=task_ids,
        message=f"已创建 {len(keyword_ids)} 个关键词、{len(task_ids)} 个任务并已异步分发评测。",
    )


# ----------------------------- 2) 任务状态查询 -----------------------------


def _fetch_task(session: Session, task_id: str) -> Optional[SearchTasks]:
    """task_id 可能是 search_task_id(int) 或 celery_task_id(str)，二者都查。"""
    by_celery = session.exec(
        select(SearchTasks).where(SearchTasks.celery_task_id == task_id)
    ).first()
    if by_celery is not None:
        return by_celery
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        return None
    return session.get(SearchTasks, tid)


def _task_status_view(session: Session, task: SearchTasks) -> TaskStatusView:
    score_total = None
    if task.status == TaskStatus.SUCCESS:
        res = session.exec(
            select(GEOResults)
            .where(GEOResults.task_id == task.id)
            .order_by(GEOResults.created_at.desc())
        ).first()
        if res is not None:
            score_total = res.score_total
    return TaskStatusView(
        task_id=task.id,
        keyword_id=task.keyword_id,
        model_name=task.model_name,
        status=task.status.value,
        celery_task_id=task.celery_task_id,
        error_message=task.error_message,
        score_total=score_total,
        created_at=task.created_at.isoformat() if task.created_at else None,
        updated_at=task.updated_at.isoformat() if task.updated_at else None,
    )


@router.get("/tasks/{task_id}/status", dependencies=[Depends(verify_api_key)])
async def get_task_status(
    task_id: str,
    ids: Optional[List[int]] = Query(None, description="批量查询的 search_task_id 列表"),
):
    """查询单条任务状态；传入 ids 时返回批量视图。

    task_id 支持两种身份：
      - search_task_id（整数，如 /tasks/12/status）
      - celery_task_id（队列返回的字符串，如 /tasks/8a1b.../status）
    """
    with Session(engine) as session:
        if ids:
            rows = session.exec(
                select(SearchTasks).where(SearchTasks.id.in_(ids))
            ).all()
            # 批量场景直接返回视图列表
            return [
                _task_status_view(session, t).model_dump() for t in rows  # type: ignore[return-value]
            ]
        task = _fetch_task(session, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail=f"未找到任务: {task_id}")
        return _task_status_view(session, task)


# ----------------------------- 3) GEO 报表聚合 -----------------------------


@router.get("/reports/{keyword_id}", dependencies=[Depends(verify_api_key)])
async def get_report(keyword_id: int):
    """聚合某关键词在各模型下的最新 GEOResults，输出结构化 GEO 报表。"""
    with Session(engine) as session:
        keyword = session.get(Keywords, keyword_id)
        if keyword is None:
            raise HTTPException(status_code=404, detail=f"Keyword id={keyword_id} 不存在")

        results = session.exec(
            select(GEOResults)
            .where(GEOResults.keyword_id == keyword_id)
            .order_by(GEOResults.created_at.desc())
        ).all()

        # 取每个 model_name 的最新一条（已按 created_at 降序）
        latest_by_model: dict[str, GEOResults] = {}
        for r in results:
            latest_by_model.setdefault(r.model_name, r)

        target_set = {d.lower().strip() for d in keyword.target_domains}
        models_report: List[dict] = []
        for model_name, r in latest_by_model.items():
            # 命中目标域名的引用链接
            hit_urls: List[str] = []
            for c in (r.citations_json or []):
                url = (c or {}).get("url", "")
                if not url:
                    continue
                netloc = extract_domain(url)
                if any(netloc == td or netloc.endswith("." + td) for td in target_set):
                    hit_urls.append(url)

            models_report.append(
                {
                    "model_name": model_name,
                    "score_total": r.score_total,
                    "score_link": r.score_link,
                    "score_mention": r.score_mention,
                    "score_position": r.score_position,
                    "matched_domains": r.matched_domains,
                    "citation_count": len(r.citations_json or []),
                    "raw_text_snapshot": (r.raw_text or "")[:2000],
                    "hit_target_urls": hit_urls,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
            )

        average = (
            sum(m["score_total"] for m in models_report) / len(models_report)
            if models_report
            else 0.0
        )

        return {
            "keyword_id": keyword_id,
            "keyword": keyword.keyword,
            "target_domains": keyword.target_domains,
            "models_covered": len(models_report),
            "average_score_total": round(average, 2),
            "report_generated_at": dt.datetime.utcnow().isoformat(),
            "models": models_report,
        }
