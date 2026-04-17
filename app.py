from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re

import streamlit as st
from docx import Document
from dotenv import find_dotenv, load_dotenv
from pypdf import PdfReader

from src.agents.analyzer import MatchAnalyzerAgent
from src.agents.rewriter import ResumeRewriterAgent
from src.config import Settings
from src.exporter import build_report_markdown
from src.llm.client import DeepSeekClient


# Always load .env from current project directory and allow overriding stale values.
dotenv_path = find_dotenv(".env", usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path, override=True)
else:
    fallback = Path(__file__).resolve().parent / ".env"
    if fallback.exists():
        load_dotenv(dotenv_path=str(fallback), override=True)
    else:
        load_dotenv(override=True)


def build_services() -> tuple[MatchAnalyzerAgent, ResumeRewriterAgent, Settings]:
    settings = Settings.from_env()
    client = DeepSeekClient(settings)
    analyzer = MatchAnalyzerAgent(client)
    rewriter = ResumeRewriterAgent(client)
    return analyzer, rewriter, settings


def _read_txt_or_md(file_bytes: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="ignore")


def _read_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _read_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def parse_resume_file(uploaded_file) -> str:
    file_bytes = uploaded_file.getvalue()
    suffix = uploaded_file.name.lower().rsplit(".", maxsplit=1)[-1]

    if suffix in {"txt", "md"}:
        return _read_txt_or_md(file_bytes)
    if suffix == "docx":
        return _read_docx(file_bytes)
    if suffix == "pdf":
        return _read_pdf(file_bytes)

    raise ValueError("Unsupported file type. Please upload .txt, .md, .docx, or .pdf")


def unwrap_markdown_fence(text: str) -> str:
    cleaned = text.lstrip("\ufeff").strip()

    # Repeatedly strip outer fenced blocks like ```markdown ... ``` or ~~~ ... ~~~.
    for _ in range(5):
        lines = cleaned.splitlines()
        if len(lines) < 2:
            break

        opening = lines[0].strip()
        closing = lines[-1].strip()
        open_match = re.fullmatch(r"(`{3,}|~{3,})[^\r\n]*", opening)
        if not open_match:
            break

        fence_token = open_match.group(1)
        fence_char = fence_token[0]
        min_len = len(fence_token)
        close_match = re.fullmatch(rf"{re.escape(fence_char)}{{{min_len},}}", closing)
        if not close_match:
            break

        cleaned = "\n".join(lines[1:-1]).lstrip("\ufeff").strip()

    return cleaned


def render_analysis(analysis, language: str) -> None:
    is_zh = language.startswith("Chinese")

    title = "匹配分析结果" if is_zh else "Match Analysis"
    score_label = "匹配得分" if is_zh else "Match Score"
    highlights_label = "匹配亮点" if is_zh else "Highlights"
    gaps_label = "主要缺口" if is_zh else "Major Gaps"
    suggestions_label = "优化建议" if is_zh else "Optimization Suggestions"

    st.subheader(title)
    st.metric(score_label, f"{analysis.score}/100")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**{highlights_label}**")
        for item in analysis.highlights:
            st.write(f"- {item}")
    with col2:
        st.markdown(f"**{gaps_label}**")
        for item in analysis.gaps:
            st.write(f"- {item}")
    with col3:
        st.markdown(f"**{suggestions_label}**")
        for item in analysis.suggestions:
            st.write(f"- {item}")


def main() -> None:
    st.set_page_config(page_title="Resume Optimizer Agent", layout="wide")
    st.title("Resume Optimizer Agent")
    st.caption("Upload/paste a resume, provide a JD, analyze fit, then generate an optimized version.")

    analyzer, rewriter, settings = build_services()

    with st.sidebar:
        st.markdown("### Runtime Config")
        if settings.deepseek_api_key:
            st.success("DEEPSEEK_API_KEY loaded")
        else:
            st.error("DEEPSEEK_API_KEY missing")
        st.write(f"Model: `{settings.model_name}`")

    input_mode = st.radio("Resume Input Mode", ["Upload file", "Paste text"], horizontal=True)

    resume_text = ""
    if input_mode == "Upload file":
        uploaded_file = st.file_uploader("Upload resume (.txt/.md/.docx/.pdf)", type=["txt", "md", "docx", "pdf"])
        if uploaded_file is not None:
            try:
                resume_text = parse_resume_file(uploaded_file)
                st.text_area("Parsed Resume Preview", value=resume_text, height=220)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Failed to read uploaded file: {exc}")
    else:
        resume_text = st.text_area("Paste resume content", height=260)

    jd_text = st.text_area("Target Job Description (JD)", height=260)

    analyze_clicked = st.button("Analyze Match")
    if analyze_clicked:
        if not resume_text.strip() or not jd_text.strip():
            st.error("Please provide both resume content and JD.")
        else:
            with st.spinner("Analyzing resume and JD match..."):
                try:
                    analysis = analyzer.analyze(resume_text, jd_text)
                    analysis_language = analyzer.detect_jd_language(jd_text)
                    st.session_state["analysis"] = analysis
                    st.session_state["analysis_language"] = analysis_language
                    st.session_state["resume_text"] = resume_text
                    st.session_state["jd_text"] = jd_text
                    st.session_state.pop("optimized_resume", None)
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Analysis failed: {exc}")

    analysis = st.session_state.get("analysis")
    if analysis:
        analysis_language = st.session_state.get("analysis_language", "English")
        render_analysis(analysis, analysis_language)

        if st.button("Confirm and Generate Optimized Resume"):
            with st.spinner("Generating optimized resume..."):
                try:
                    optimized_resume = rewriter.rewrite(
                        st.session_state["resume_text"],
                        st.session_state["jd_text"],
                        analysis.suggestions,
                    )
                    st.session_state["optimized_resume"] = unwrap_markdown_fence(optimized_resume)
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Resume generation failed: {exc}")

    optimized_resume_raw = st.session_state.get("optimized_resume")
    optimized_resume = unwrap_markdown_fence(optimized_resume_raw) if optimized_resume_raw else ""
    if optimized_resume_raw and optimized_resume_raw != optimized_resume:
        st.session_state["optimized_resume"] = optimized_resume

    if optimized_resume:
        st.subheader("Optimized Resume")
        with st.container(height=360, border=True):
            st.markdown(optimized_resume)

        st.download_button(
            "Download optimized resume (.md)",
            data=optimized_resume.encode("utf-8"),
            file_name="optimized_resume.md",
            mime="text/markdown",
        )

        report = build_report_markdown(st.session_state["analysis"], optimized_resume)
        st.download_button(
            "Download full report (.md)",
            data=report.encode("utf-8"),
            file_name="resume_optimization_report.md",
            mime="text/markdown",
        )


if __name__ == "__main__":
    main()
