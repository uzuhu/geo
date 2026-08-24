"""大模型适配层（阶段二 模块A：官方 API 直连通道）。

统一抽象基类 + 各平台异步 client + 工厂。
"""
from app.llm.base import LLMClient

__all__ = ["LLMClient"]
