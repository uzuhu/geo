"""FastAPI 应用入口（阶段五：挂载交付接口）。

启动生命周期：服务启动时尝试建表（首次运行）；若数据库不可达仅打印告警，
保证 /health 仍可用，便于在依赖未就绪时先联调无 DB 的路由。
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.core.config import settings
from app.db.engine import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 首次运行建表（生产环境建议用 Alembic 管理迁移）
    try:
        init_db()
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] 数据库初始化失败，依赖 DB 的接口将不可用: {exc}")
    yield


app = FastAPI(title=settings.APP_NAME, version="0.1.0", lifespan=lifespan)

# 阶段五交付接口：挂载到 /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}
