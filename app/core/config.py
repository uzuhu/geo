"""全局配置（基于 pydantic-settings，从 .env 加载）。"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# 默认动态 User-Agent 池（浏览器通道反爬用，可在 .env 覆盖）
_DEFAULT_UAS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True
    )

    # ----- App -----
    APP_NAME: str = "GEO Monitor"
    DEBUG: bool = False

    # ----- 系统级 API 鉴权（阶段六：公网防刷） -----
    # 公网部署时务必在 .env 中覆盖为强随机值；客户端请求须携带 X-API-Key 头。
    # 若保持为空，verify_api_key 会拒绝一切请求，避免裸奔上线。
    GEO_SYSTEM_AUTH_KEY: str = "GEO_SYS_8Kp2mQx9vLw3nRz7tBc5dFg1hJy6sUu0eN4aC8oI2p"

    # ----- OpenAI (GPT-4o 联网模式) -----
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o"
    # 联网搜索工具参数版本：web_search_preview | web_search
    OPENAI_WEB_SEARCH_TOOL: str = "web_search_preview"

    # ----- DeepSeek-V3 API -----
    # 标准 chat API 无原生联网工具，联网实现方式待确认
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # ----- 文心一言 (ERNIE / 百度千帆) -----
    ERNIE_API_KEY: Optional[str] = None
    ERNIE_SECRET_KEY: Optional[str] = None
    ERNIE_MODEL: str = "ernie-4.0-8k"
    ERNIE_ACCESS_TOKEN_URL: str = "https://aip.baidubce.com/oauth/2.0/token"
    ERNIE_CHAT_URL: str = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/"

    # ----- Redis / Celery -----
    REDIS_URL: str = "redis://localhost:6379/0"

    # ----- PostgreSQL -----
    POSTGRES_DSN: str = "postgresql+psycopg://geo:geo@localhost:5432/geo"

    # ----- Elasticsearch -----
    ELASTICSEARCH_HOSTS: List[str] = ["http://localhost:9200"]

    # ----- 浏览器自动化 -----
    BROWSER_HEADLESS: bool = True
    PROXY_URL: Optional[str] = None
    BROWSER_MAX_CONCURRENCY: int = 3
    USER_AGENTS: List[str] = _DEFAULT_UAS


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
