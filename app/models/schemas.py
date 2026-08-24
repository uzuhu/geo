"""统一数据模型（阶段二/三共用）。

LLMResponse 是 API 直连通道与浏览器通道共同的返回结构，
下游解析/评分引擎（阶段三）直接消费此结构。
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """一条被引用的信源链接。"""

    url: str
    title: Optional[str] = None
    rank: Optional[int] = Field(
        default=None, description="在参考信源列表中的排序（用于首屏首位度评分）"
    )


class LLMResponse(BaseModel):
    """所有适配层（API 直连 + 浏览器）统一的返回结构。"""

    provider: str = Field(..., description="通道标识，如 openai / deepseek / browser:perplexity")
    model: str = Field(..., description="实际使用的模型或站点")
    text: str = Field(default="", description="AI 回答主体纯文本")
    citations: List[Citation] = Field(default_factory=list, description="被引用的信源链接列表")
    usage: Optional[dict] = None
    raw: Optional[dict] = None
    error: Optional[str] = Field(default=None, description="通道级错误（非空表示本次查询失败）")
