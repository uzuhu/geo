"""client 工厂：根据配置实例化可用的直连通道。"""
from __future__ import annotations

from typing import List, Optional

from app.core.config import settings
from app.llm.base import LLMClient


async def build_clients(enabled: Optional[List[str]] = None) -> List[LLMClient]:
    """构建启用的 API 直连 client 列表。

    Args:
        enabled: 指定仅构建哪些通道（如 ["openai", "ernie"]）。
                 为 None 时构建所有配置了 key 的通道。
    """
    # 延迟导入，避免循环依赖 / 未安装 SDK 时整体报错
    from app.llm.openai_client import OpenAIClient
    from app.llm.deepseek_client import DeepSeekClient
    from app.llm.ernie_client import ErnieClient

    builders = {
        "openai": lambda: OpenAIClient(
            settings.OPENAI_API_KEY, settings.OPENAI_BASE_URL, settings.OPENAI_MODEL
        ),
        "deepseek": lambda: DeepSeekClient(
            settings.DEEPSEEK_API_KEY, settings.DEEPSEEK_BASE_URL, settings.DEEPSEEK_MODEL
        ),
        "ernie": lambda: ErnieClient(
            settings.ERNIE_API_KEY, settings.ERNIE_SECRET_KEY, settings.ERNIE_MODEL
        ),
    }

    clients: List[LLMClient] = []
    for name, build in builders.items():
        if enabled and name not in enabled:
            continue
        try:
            clients.append(build())
        except ValueError:
            # 缺少 key 的通道静默跳过
            continue
    return clients
