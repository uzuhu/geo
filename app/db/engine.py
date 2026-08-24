"""数据库引擎与会话工厂（阶段四）。"""
from __future__ import annotations

from typing import Iterator

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine: Engine = create_engine(
    settings.POSTGRES_DSN,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    future=True,
)


def init_db() -> None:
    """建表（首次运行）。生产环境建议用 Alembic 管理迁移。"""
    # 导入模型以确保元数据注册
    from app.models import db  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI 依赖注入用。"""
    with Session(engine) as session:
        yield session
