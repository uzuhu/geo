"""通用网页对话提取器（阶段二 模块B 核心逻辑）。

目标站点：Perplexity、秘塔 AI 等原生 AI 搜索引擎。
流程：启动 Chromium -> 导航 -> 模拟人工键入 -> 等待渲染 -> 抓取回答 + 引用链接。

注意：各站点的输入框 / 答案 / 引用选择器（见 SITE_PRESETS）采用「基于特征的逗号容错
匹配」，对前端改版有较强抗穿透能力；若需更精准，可按目标平台真实 DOM 微调列表顺序。
"""
from __future__ import annotations

import asyncio
import random
from typing import List, Optional

from playwright.async_api import Browser, Page, async_playwright

from app.browser.stealth import apply_stealth, get_random_user_agent
from app.core.config import settings
from app.models.schemas import Citation, LLMResponse

# 各 AI 搜索站点的预设。
# 选择器采用「基于特征的逗号容错列表」：Playwright 会命中第一个存在的元素，
# 因此即便前端改版把 class/testid 换了，只要特征（占位符关键字 / 语义标签）还在，
# 提取流程就不会被击穿。人工校对真实 DOM 后，可进一步收紧列表顺序。
SITE_PRESETS = {
    "perplexity": {
        "url": "https://www.perplexity.ai",
        # 输入框：优先带 Ask/问题 占位符的 textarea，兜底任意 textarea
        "input_selector": 'textarea[placeholder*="Ask"], textarea[placeholder*="问题"], textarea',
        # 答案区：优先 prose 容器，兜底 article
        "answer_selector": "div.prose, .prose, article",
        # 引用链接：所有外链，排除站点自身域名
        "citation_selector": 'a[href^="http"]:not([href*="perplexity.ai"])',
        "submit": "Enter",
    },
    "metaso": {  # 秘塔 AI
        "url": "https://metaso.cn",
        # 输入框：textarea 或 contenteditable 输入框
        "input_selector": 'textarea, div[contenteditable="true"]',
        # 答案区：优先 markdown-body / answer-content，兜底 article
        "answer_selector": ".markdown-body, .answer-content, article",
        # 引用链接：来源条目 / 参考列表中的链接，或任何非站点自身的外链
        "citation_selector": '.source-item a, .reference-list a, a[href^="http"]:not([href*="metaso.cn"])',
        "submit": "Enter",
    },
}


class WebSearchExtractor:
    """针对单个 AI 搜索站点的无头浏览器提取器。"""

    def __init__(self, site: str = "perplexity", proxy: Optional[str] = None) -> None:
        if site not in SITE_PRESETS:
            raise ValueError(f"未知站点: {site}，可选 {list(SITE_PRESETS)}")
        self.preset = SITE_PRESETS[site]
        self.proxy = proxy or settings.PROXY_URL
        self._playwright = None
        self._browser: Optional[Browser] = None

    async def _ensure_browser(self) -> None:
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=settings.BROWSER_HEADLESS,
                proxy={"server": self.proxy} if self.proxy else None,
                args=["--disable-blink-features=AutomationControlled"],
            )

    async def query(self, prompt: str, *, timeout: int = 60) -> LLMResponse:
        """执行一次查询并返回 LLMResponse。"""
        await self._ensure_browser()
        context = await self._browser.new_context(
            user_agent=get_random_user_agent(),
            viewport={"width": 1280, "height": 900},
        )
        page: Page = await context.new_page()
        provider = f"browser:{self.preset['url']}"
        try:
            await apply_stealth(page)
            await page.goto(self.preset["url"], wait_until="domcontentloaded", timeout=timeout * 1000)

            # 定位输入框，随机延迟模拟人工逐字键入
            box = await page.wait_for_selector(self.preset["input_selector"], timeout=timeout * 1000)
            for ch in prompt:
                await box.type(ch, delay=random.uniform(30, 120))
            await page.keyboard.press(self.preset["submit"])

            # 等待回答渲染完成：答案节点出现 + 文本停止增长
            await page.wait_for_selector(self.preset["answer_selector"], timeout=timeout * 1000)
            answer = await self._wait_until_stable(page, self.preset["answer_selector"], timeout=timeout)

            # 关键抓取：引用链接 + 标题
            citations = await self._extract_citations(page)
            return LLMResponse(
                provider=provider,
                model=self.preset["url"],
                text=answer,
                citations=citations,
            )
        except Exception as exc:  # 通道级异常统一兜底（运行前自检点 #2）
            return LLMResponse(provider=provider, model=self.preset["url"], text="", error=str(exc))
        finally:
            await context.close()

    async def _wait_until_stable(self, page: Page, selector: str, timeout: int) -> str:
        """轮询答案文本，直到在 2s 内长度不再变化，视为渲染完成。"""
        last = ""
        stable_for = 0.0
        step = 0.5
        elapsed = 0.0
        while elapsed < timeout:
            try:
                text = (await page.locator(selector).first.inner_text()) or ""
            except Exception:
                text = ""
            if text == last:
                stable_for += step
                if stable_for >= 2.0:
                    return text
            else:
                stable_for = 0.0
                last = text
            await asyncio.sleep(step)
            elapsed += step
        return last

    async def _extract_citations(self, page: Page) -> List[Citation]:
        """提取回答主体中的 <a> 外链与其可见文本作为标题，并记录排序。"""
        elements = await page.locator(self.preset["citation_selector"]).all()
        citations: List[Citation] = []
        seen = set()
        for rank, el in enumerate(elements, start=1):
            try:
                href = await el.get_attribute("href")
                if not href or href in seen:
                    continue
                seen.add(href)
                title = (await el.inner_text()).strip() or None
                citations.append(Citation(url=href, title=title, rank=rank))
            except Exception:
                continue
        return citations

    async def close(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None
