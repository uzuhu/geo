"""DeepSeek 直连通道。

重要：DeepSeek 标准 chat API 没有原生联网搜索工具。
按确认的接入方式，这里采用「prompt 伪联网」——在 system 指令中要求基于最新网络信息回答，
并兜底从回答文本里正则提取引用链接。supports_native_web_search=False。
后续若接入带联网的第三方兼容端点，可改为原生 tools。
"""
from __future__ import annotations

import re
from typing import List, Optional

from openai import AsyncOpenAI

from app.llm.base import LLMClient
from app.models.schemas import Citation, LLMResponse

_WEB_SEARCH_SYSTEM = (
    "你是一个联网搜索助手。请基于最新的网络公开信息作答，"
    "并在回答中尽可能附上相关的引用链接（URL），以便核对来源。"
)


class DeepSeekClient(LLMClient):
    name = "deepseek"
    supports_native_web_search = False

    def __init__(self, api_key: str, base_url: Optional[str] = None, model: Optional[str] = None, **kwargs) -> None:
        super().__init__(api_key, base_url, model, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def call_llm(self, prompt: str, *, enable_web_search: bool = True, **kwargs) -> LLMResponse:
        messages = []
        if enable_web_search:
            messages.append({"role": "system", "content": _WEB_SEARCH_SYSTEM})
        messages.append({"role": "user", "content": prompt})

        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **{k: v for k, v in kwargs.items() if k != "enable_web_search"},
            )
            text = resp.choices[0].message.content or ""
            citations = self._extract_links(text)
            usage = resp.usage.model_dump() if resp.usage else None
            raw = resp.model_dump() if hasattr(resp, "model_dump") else None
            return LLMResponse(
                provider=self.name, model=self.model, text=text,
                citations=citations, usage=usage, raw=raw,
            )
        except Exception as exc:  # 联网参数异常捕获（运行前自检点 #2）
            return LLMResponse(provider=self.name, model=self.model, text="", error=str(exc))

    @staticmethod
    def _extract_links(text: str) -> List[Citation]:
        """伪联网兜底：从回答文本正则提取 URL 作为引用。"""
        urls = re.findall(r"https?://[^\s)>\]\"']+", text)
        seen: set[str] = set()
        out: List[Citation] = []
        for rank, url in enumerate(urls, start=1):
            if url in seen:
                continue
            seen.add(url)
            out.append(Citation(url=url, rank=rank))
        return out

    async def close(self) -> None:
        await self.client.close()
