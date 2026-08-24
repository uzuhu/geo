"""文心一言（ERNIE / 百度千帆）直连通道。

按确认的接入方式：使用百度智能云千帆 SDK，并通过 enable_search=True 显式开启联网搜索。
引用链接从千帆返回的 search_results 中提取。
鉴权由千帆 SDK 读取 QIANFAN_ACCESS_KEY / QIANFAN_SECRET_KEY 环境变量，故在初始化时写入。
"""
from __future__ import annotations

import asyncio
import os
from typing import List, Optional

from app.core.config import settings
from app.llm.base import LLMClient
from app.models.schemas import Citation, LLMResponse


class ErnieClient(LLMClient):
    name = "ernie"
    supports_native_web_search = True

    def __init__(self, api_key: str, secret_key: Optional[str] = None, model: Optional[str] = None, **kwargs) -> None:
        if not api_key:
            raise ValueError(f"[{self.name}] 初始化失败：缺少 API Key")
        self.api_key = api_key
        self.secret_key = secret_key
        self.model = model or settings.ERNIE_MODEL
        # 千帆 SDK 从环境变量读取鉴权
        os.environ["QIANFAN_ACCESS_KEY"] = api_key
        if secret_key:
            os.environ["QIANFAN_SECRET_KEY"] = secret_key
        self._chat = None  # 延迟到首次调用时构建，避免未安装 SDK 即报错

    async def call_llm(self, prompt: str, *, enable_web_search: bool = True, **kwargs) -> LLMResponse:
        try:
            from qianfan import ChatCompletion

            if self._chat is None:
                self._chat = ChatCompletion()

            # 千帆 SDK 同步接口，用线程池保持 call_llm 的异步语义
            resp = await asyncio.to_thread(
                self._chat.completion,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                enable_search=enable_web_search,
                **kwargs,
            )

            body = resp if isinstance(resp, dict) else getattr(resp, "body", resp)
            text = (body.get("result") if isinstance(body, dict) else getattr(body, "result", "")) or ""
            citations = self._extract_citations(body)
            return LLMResponse(
                provider=self.name, model=self.model, text=text,
                citations=citations, raw=body if isinstance(body, dict) else None,
            )
        except Exception as exc:  # 联网参数异常捕获（运行前自检点 #2）
            return LLMResponse(provider=self.name, model=self.model, text="", error=str(exc))

    @staticmethod
    def _extract_citations(body) -> List[Citation]:
        """从千帆 enable_search 返回的 search_results 提取引用。"""
        if not isinstance(body, dict):
            body = getattr(body, "body", {}) or {}
        results = body.get("search_results") or []
        out: List[Citation] = []
        for rank, item in enumerate(results, start=1):
            url = (item.get("url") or item.get("link")) if isinstance(item, dict) else None
            if url:
                title = item.get("title") if isinstance(item, dict) else None
                out.append(Citation(url=url, title=title, rank=rank))
        return out

    async def close(self) -> None:
        self._chat = None
