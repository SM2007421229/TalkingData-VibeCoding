from __future__ import annotations

from pathlib import Path

from src.llm.client import DeepSeekClient


class ResumeRewriterAgent:
    def __init__(self, client: DeepSeekClient) -> None:
        self._client = client
        self._system_prompt = (
            "You rewrite resumes to be stronger and clearer without fabricating facts. "
            "Keep claims grounded in the original resume."
        )
        self._template = (Path(__file__).resolve().parents[1] / "prompts" / "rewrite_prompt.txt").read_text(
            encoding="utf-8"
        )

    def rewrite(self, resume_text: str, jd_text: str, suggestions: list[str]) -> str:
        suggestions_text = "\n".join(f"- {item}" for item in suggestions)
        prompt = self._template.format(
            resume=resume_text.strip(),
            jd=jd_text.strip(),
            suggestions=suggestions_text if suggestions_text else "- No additional suggestions",
        )
        return self._client.chat_text(self._system_prompt, prompt)
