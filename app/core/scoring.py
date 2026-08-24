"""GEO 核心解析与评分引擎（阶段三）。

解析器：
- 域名级匹配：把 Citation 的 URL 与 Keywords 绑定的目标域名做匹配。
- 关键词/品牌词检测：词频统计 + 首段命中检测（正向提及）。

评分算法 calculate_geo_score（满分 100）：
- 链接引用权重 50 分（含首位度加分）：命中目标域名得 40，首位引用命中再 +10。
- 关键词提及 30 分：每提及一次目标关键词得 10 分，上限 30。
- 首屏首段推荐 20 分：回答首段包含目标关键词或目标域名链接，得 20。
"""
from __future__ import annotations

import re
from typing import List

from pydantic import BaseModel, Field

from app.models.schemas import LLMResponse


# ----------------------------- 解析器工具 -----------------------------


def extract_domain(url: str) -> str:
    """从 URL 提取注册域名并去掉 www. 前缀。"""
    from urllib.parse import urlparse

    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def _normalize(domain: str) -> str:
    d = domain.lower().strip()
    if d.startswith("www."):
        d = d[4:]
    return d


def is_target_match(citation_domain: str, target_domains: List[str]) -> bool:
    """域名级匹配：精确相等或为其子域。"""
    cd = _normalize(citation_domain)
    for t in target_domains:
        td = _normalize(t)
        if cd == td or cd.endswith("." + td):
            return True
    return False


def count_mentions(text: str, term: str) -> int:
    """不区分大小写统计关键词出现次数。"""
    if not term:
        return 0
    return len(re.findall(re.escape(term), text, flags=re.IGNORECASE))


def first_paragraph(text: str) -> str:
    """返回回答的首个非空段落。"""
    paras = [p.strip() for p in re.split(r"\n\s*\n|[\r\n]+", text or "") if p.strip()]
    return paras[0] if paras else ""


# ----------------------------- 评分对象 -----------------------------


class GEOScore(BaseModel):
    keyword: str
    target_domains: List[str]

    citation_count: int = 0
    matched_citation_count: int = 0
    matched_domains: List[str] = Field(default_factory=list)
    first_citation_is_target: bool = False

    mention_count: int = 0
    first_paragraph_has_target: bool = False

    score_link: float = 0.0
    score_mention: float = 0.0
    score_position: float = 0.0
    score_total: float = 0.0


# ----------------------------- 主算法 -----------------------------


def calculate_geo_score(
    response: LLMResponse,
    keyword: str,
    target_domains: List[str],
) -> GEOScore:
    """对一次 LLMResponse 计算 GEO 综合得分。"""
    text = response.text or ""
    citations = response.citations or []

    # 1) 域名级引用匹配
    matched = [c for c in citations if is_target_match(c.url, target_domains)]
    matched_domains = sorted({extract_domain(c.url) for c in matched})
    first_citation_is_target = bool(citations) and is_target_match(citations[0].url, target_domains)

    # 2) 关键词提及（正向提及）
    mention_count = count_mentions(text, keyword)

    # 3) 首屏首段推荐：首段含目标关键词，或首段出现目标域名链接
    fp = first_paragraph(text)
    fp_urls = re.findall(r"https?://[^\s)>\]]+", fp)
    first_paragraph_has_target = bool(
        (keyword and re.search(re.escape(keyword), fp, re.IGNORECASE))
        or any(is_target_match(extract_domain(u), target_domains) for u in fp_urls)
    )

    # ----------------- 权重计算（满分 100） -----------------
    # 链接引用权重 50 分（含首位度加分）
    score_link = 0.0
    if matched:
        score_link = 40.0
        if first_citation_is_target:
            score_link += 10.0
        score_link = min(score_link, 50.0)

    # 关键词提及 30 分：每次 10 分，上限 30
    score_mention = min(mention_count * 10.0, 30.0)

    # 首屏首段推荐 20 分
    score_position = 20.0 if first_paragraph_has_target else 0.0

    score_total = score_link + score_mention + score_position

    return GEOScore(
        keyword=keyword,
        target_domains=target_domains,
        citation_count=len(citations),
        matched_citation_count=len(matched),
        matched_domains=matched_domains,
        first_citation_is_target=first_citation_is_target,
        mention_count=mention_count,
        first_paragraph_has_target=first_paragraph_has_target,
        score_link=score_link,
        score_mention=score_mention,
        score_position=score_position,
        score_total=score_total,
    )
