from __future__ import annotations

import os
from dataclasses import dataclass


def _get_env(name: str, default: str = "") -> str:
    # Be tolerant to UTF-8 BOM in .env key names (common on Windows editors).
    value = os.getenv(name)
    if value is None:
        value = os.getenv(f"\ufeff{name}")
    if value is None:
        value = default
    return value.strip()


@dataclass(frozen=True)
class Settings:
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    model_name: str = "deepseek-chat"
    request_timeout: int = 90

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = _get_env("DEEPSEEK_API_KEY")
        base_url = _get_env("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        model_name = _get_env("MODEL_NAME", "deepseek-chat")
        timeout_raw = _get_env("REQUEST_TIMEOUT", "90")

        try:
            timeout = int(timeout_raw)
        except ValueError:
            timeout = 90

        return cls(
            deepseek_api_key=api_key,
            deepseek_base_url=base_url.rstrip("/"),
            model_name=model_name,
            request_timeout=timeout,
        )
