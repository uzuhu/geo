"""SQLModel 数据模型层（阶段四 4.2）。

三张核心表：
- Keywords：待查词、监控频率、绑定的目标域名。
- SearchTasks：单次查询任务状态机（PENDING/RUNNING/SUCCESS/FAILED）+ 失败原因。
- GEOResults：AI 回答纯文本快照、被引用 URL 列表(JSON)、各维度得分与综合 GEO 得分、时间戳。
"""
from __future__ import annotations

import datetime as dt
from enum import Enum
from typing import List, Optional

from sqlalchemy import JSON, Column, Enum as SAEnum, ForeignKey
from sqlmodel import Field, SQLModel


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Keywords(SQLModel, table=True):
    __tablename__ = "keywords"

    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True, description="待监测的关键词 / 品牌词")
    # 用户绑定的目标域名（用于引文域名级匹配），如 ["example.com", "www.brand.cn"]
    target_domains: List[str] = Field(
        default_factory=list, sa_column=Column(JSON), description="目标域名列表"
    )
    monitor_frequency: str = Field(
        default="daily", description="监控频率：hourly / daily / weekly"
    )
    is_active: bool = Field(default=True, index=True)
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    updated_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)


class SearchTasks(SQLModel, table=True):
    __tablename__ = "search_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    keyword_id: int = Field(index=True, foreign_key="keywords.id")
    model_name: str = Field(index=True, description="openai / deepseek / ernie / perplexity / metaso")
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        sa_column=Column(SAEnum(TaskStatus, native_enum=False), nullable=False, index=True),
    )
    error_message: Optional[str] = Field(default=None, description="失败原因")
    celery_task_id: Optional[str] = Field(default=None, description="Celery 任务 ID，便于追踪")
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    updated_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)


class GEOResults(SQLModel, table=True):
    __tablename__ = "geo_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(index=True, foreign_key="search_tasks.id")
    keyword_id: int = Field(index=True, foreign_key="keywords.id")
    model_name: str = Field(index=True)
    provider: str = Field(default="", description="api / browser")

    raw_text: str = Field(default="", description="AI 回答纯文本快照")
    citations_json: List[dict] = Field(
        default_factory=list, sa_column=Column(JSON), description="被引用的具体 URL 列表"
    )

    # 各维度得分（满分 100）
    score_link: float = Field(default=0.0, description="链接引用权重（含首位度加分），0-50")
    score_mention: float = Field(default=0.0, description="关键词提及，0-30")
    score_position: float = Field(default=0.0, description="首屏首段推荐，0-20")
    score_total: float = Field(default=0.0, index=True, description="综合 GEO 得分")

    matched_domains: List[str] = Field(
        default_factory=list, sa_column=Column(JSON), description="命中的目标域名"
    )
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
