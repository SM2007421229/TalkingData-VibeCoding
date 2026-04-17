from __future__ import annotations

import json
from typing import Any

import requests

from src.config import Settings


class DeepSeekClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self._settings.deepseek_api_key:
            raise ValueError("Missing DEEPSEEK_API_KEY. Configure it as an environment variable.")

        payload = {
            "model": self._settings.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        url = f"{self._settings.deepseek_base_url}/chat/completions"
        response = requests.post(
            url,
            headers=self._headers(),
            json=payload,
            timeout=self._settings.request_timeout,
        )
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)

    def chat_text(self, system_prompt: str, user_prompt: str) -> str:
        if not self._settings.deepseek_api_key:
            raise ValueError("Missing DEEPSEEK_API_KEY. Configure it as an environment variable.")

        payload = {
            "model": self._settings.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.4,
        }

        url = f"{self._settings.deepseek_base_url}/chat/completions"
        response = requests.post(
            url,
            headers=self._headers(),
            json=payload,
            timeout=self._settings.request_timeout,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
