"""OpenAI 直连通道（GPT-4o 联网模式）。

硬性要求：显式开启 web_search_preview 联网工具（由 settings.OPENAI_WEB_SEARCH_TOOL 控制版本）。
引用链接从 web search 的 url_citation 注解中提取。
"""
from __future__ import annotations

from typing import List, Optional

from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.base import LLMClient
from app.models.schemas import Citation, LLMResponse


class OpenAIClient(LLMClient):
    name = "openai"
    supports_native_web_search = True

    def __init__(self, api_key: str, base_url: Optional[str] = None, model: Optional[str] = None, **kwargs) -> None:
        super().__init__(api_key, base_url, model, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def call_llm(self, prompt: str, *, enable_web_search: bool = True, **kwargs) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        tools = None
        if enable_web_search:
            # 显式开启联网搜索工具（核心硬性要求）
            tools = [{"type": settings.OPENAI_WEB_SEARCH_TOOL, "search_context_size": "medium"}]

        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
                **{k: v for k, v in kwargs.items() if k != "enable_web_search"},
            )
            msg = resp.choices[0].message
            text = msg.content or ""
            citations = self._extract_citations(msg)
            usage = resp.usage.model_dump() if resp.usage else None
            raw = resp.model_dump() if hasattr(resp, "model_dump") else None
            return LLMResponse(
                provider=self.name, model=self.model, text=text,
                citations=citations, usage=usage, raw=raw,
            )
        except Exception as exc:  # 联网参数异常捕获（运行前自检点 #2）
            return LLMResponse(provider=self.name, model=self.model, text="", error=str(exc))

    @staticmethod
    def _extract_citations(msg) -> List[Citation]:
        out: List[Citation] = []
        # web_search_preview 通过 message.annotations 返回 url_citation
        for ann in getattr(msg, "annotations", []) or []:
            url_citation = getattr(ann, "url_citation", None)
            if url_citation:
                out.append(Citation(url=url_citation.url, title=getattr(url_citation, "title", None)))
        # 兜底：content 为分段结构时，逐段取 url_citation
        content = getattr(msg, "content", None)
        if isinstance(content, list):
            for part in content:
                ann = getattr(part, "url_citation", None)
                if ann and getattr(ann, "url", None):
                    out.append(Citation(url=ann.url, title=getattr(ann, "title", None)))
        return out

    async def close(self) -> None:
        await self.client.close()
