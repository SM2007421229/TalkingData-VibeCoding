from __future__ import annotations

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    score: int = Field(ge=0, le=100)
    highlights: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class RewriteResult(BaseModel):
    optimized_resume: str
