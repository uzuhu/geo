"""反爬防护：动态 User-Agent + Playwright stealth 注入。"""
from __future__ import annotations

import random
from typing import List

from app.core.config import settings


def get_random_user_agent() -> str:
    """从配置池中随机取一个 User-Agent。"""
    pool: List[str] = settings.USER_AGENTS
    return random.choice(pool)


# 在每次页面初始化时注入，抹除无头浏览器指纹特征。
STEALTH_JS = """
() => {
  // 1. 抹除 webdriver 标志
  Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  // 2. 伪造 plugins / languages
  Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
  Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
  // 3. 抹除 headless 相关全局
  delete window.__nightmare;
  // 4. chrome 对象探测兜底
  if (window.chrome === undefined) {
    window.chrome = { runtime: {} };
  }
}
"""


async def apply_stealth(page) -> None:
    """对单个 page 注入 stealth 脚本（在 goto 之前调用）。"""
    await page.add_init_script(STEALTH_JS)
