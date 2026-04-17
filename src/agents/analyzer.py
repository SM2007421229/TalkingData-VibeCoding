from __future__ import annotations

import re
from pathlib import Path

from pydantic import ValidationError

from src.llm.client import DeepSeekClient
from src.schemas import AnalysisResult


class MatchAnalyzerAgent:
    def __init__(self, client: DeepSeekClient) -> None:
        self._client = client
        self._system_prompt = (
            "You are a strict resume-vs-jd evaluator. "
            "Return factual, concise content and output only valid JSON."
        )
        self._template = (Path(__file__).resolve().parents[1] / "prompts" / "analyze_prompt.txt").read_text(
            encoding="utf-8"
        )

    @staticmethod
    def detect_jd_language(jd_text: str) -> str:
        # If JD contains CJK characters, treat as Chinese; otherwise English.
        if re.search(r"[\u4e00-\u9fff]", jd_text):
            return "Chinese (Simplified)"
        return "English"

    def analyze(self, resume_text: str, jd_text: str) -> AnalysisResult:
        target_language = self.detect_jd_language(jd_text)
        prompt = self._template.format(
            resume=resume_text.strip(),
            jd=jd_text.strip(),
            target_language=target_language,
        )
        raw = self._client.chat_json(self._system_prompt, prompt)

        try:
            return AnalysisResult.model_validate(raw)
        except ValidationError as exc:
            raise ValueError(f"Model output validation failed: {exc}") from exc
