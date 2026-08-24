"""Celery 应用（阶段一技术栈；阶段四注册异步任务）。"""
from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery("geo", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)

# 注册任务模块（阶段四：app.tasks.async_check_keyword_task）
celery_app.conf.update(include=["app.tasks"])
