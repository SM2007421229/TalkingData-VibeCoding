from __future__ import annotations

from datetime import datetime

from src.schemas import AnalysisResult


def build_report_markdown(analysis: AnalysisResult, optimized_resume: str) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Resume Optimization Report",
        "",
        f"Generated at: {now}",
        "",
        f"## Match Score: {analysis.score}/100",
        "",
        "## Highlights",
    ]
    lines.extend([f"- {item}" for item in analysis.highlights] or ["- N/A"])
    lines.append("")
    lines.append("## Major Gaps")
    lines.extend([f"- {item}" for item in analysis.gaps] or ["- N/A"])
    lines.append("")
    lines.append("## Optimization Suggestions")
    lines.extend([f"- {item}" for item in analysis.suggestions] or ["- N/A"])
    lines.append("")
    lines.append("## Optimized Resume")
    lines.append(optimized_resume.strip() or "N/A")
    lines.append("")
    return "\n".join(lines)
