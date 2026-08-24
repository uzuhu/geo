"""LLMClient 抽象基类。

所有 API 直连 client（OpenAI / DeepSeek / 文心一言）必须继承此类，
核心硬性要求：call_llm 必须在请求参数中显式开启“联网搜索”开关。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.models.schemas import LLMResponse


class LLMClient(ABC):
    """统一的 LLM 适配层抽象基类。"""

    #: 通道标识（工厂/日志用）
    name: str = "base"
    #: 是否支持平台原生联网搜索工具
    supports_native_web_search: bool = False

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> None:
        if not api_key:
            raise ValueError(f"[{self.name}] 初始化失败：缺少 API Key")
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.extra = kwargs

    @abstractmethod
    async def call_llm(self, prompt: str, *, enable_web_search: bool = True, **kwargs) -> LLMResponse:
        """调用模型并返回结构化响应（文本 + 引用）。

        Args:
            prompt: 用户输入的查询提示词。
            enable_web_search: 是否显式开启联网搜索（默认开启，硬性要求）。
        """
        raise NotImplementedError

    async def close(self) -> None:
        """释放底层资源（如 http 客户端）。子类按需重写。"""
        return None
