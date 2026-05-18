import io
from datetime import datetime
from typing import Any, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

_PRIMARY = colors.HexColor("#4F46E5")
_PRIMARY_DARK = colors.HexColor("#312E81")
_BG = colors.HexColor("#F8FAFC")
_SURFACE = colors.HexColor("#FFFFFF")
_TEXT = colors.HexColor("#1E293B")
_MUTED = colors.HexColor("#64748B")
_BORDER = colors.HexColor("#E2E8F0")
_SUCCESS = colors.HexColor("#10B981")
_WARNING = colors.HexColor("#F59E0B")
_ERROR = colors.HexColor("#EF4444")
_INFO = colors.HexColor("#2563EB")


def _build_styles():
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ReportTitle",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=_TEXT,
            spaceAfter=6,
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            fontSize=11,
            textColor=_MUTED,
            spaceAfter=4,
            alignment=TA_CENTER,
        ),
        "section": ParagraphStyle(
            "SectionHeader",
            fontSize=14,
            textColor=_TEXT,
            spaceBefore=16,
            spaceAfter=8,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "Body",
            fontSize=10,
            textColor=_TEXT,
            spaceAfter=4,
            leading=14,
        ),
        "question": ParagraphStyle(
            "Question",
            fontSize=10,
            textColor=_TEXT,
            spaceBefore=12,
            spaceAfter=4,
            fontName="Helvetica-Bold",
            leading=14,
        ),
        "answer": ParagraphStyle(
            "Answer",
            fontSize=10,
            textColor=_TEXT,
            spaceAfter=4,
            leftIndent=12,
            leading=14,
        ),
        "label": ParagraphStyle(
            "Label",
            fontSize=9,
            textColor=_MUTED,
            fontName="Helvetica-Oblique",
            spaceAfter=2,
        ),
    }


def _score_color(score: float):
    if score >= 8:
        return _SUCCESS
    if score >= 5:
        return _WARNING
    return _ERROR


def _verdict_color(verdict: str):
    v = (verdict or "").lower()
    if v == "excellent":
        return _SUCCESS
    if v == "good":
        return _INFO
    if v == "fair":
        return _WARNING
    return _ERROR


def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(_PRIMARY)
    canvas.rect(0, h - 1.2 * cm, w, 1.2 * cm, fill=True, stroke=False)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(1.5 * cm, h - 0.8 * cm, "AI Interview Prep Bot — Session Report")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 1.5 * cm, h - 0.8 * cm, f"Page {doc.page}")
    canvas.setFillColor(_MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(w / 2, 0.6 * cm, "AI Interview Prep Bot • Generated Report")
    canvas.restoreState()


def generate_pdf_report(
    questions: list[dict[str, Any]],
    answers: list[str],
    evaluations: list[dict[str, Any]],
    summary: Optional[dict[str, Any]] = None,
    meta: Optional[dict[str, Any]] = None,
) -> bytes:
    buffer = io.BytesIO()
    styles = _build_styles()

    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2.0 * cm,
        bottomMargin=1.5 * cm,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    template = PageTemplate(id="main", frames=frame, onPage=_header_footer)
    doc.addPageTemplates([template])

    story = []
    generated_at = datetime.now().strftime("%B %d, %Y at %H:%M")
    job_title = (meta or {}).get("title") or "Job Description"

    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("Interview Performance Report", styles["title"]))
    story.append(Paragraph(f"Role: {job_title}", styles["subtitle"]))
    story.append(Paragraph(f"Generated: {generated_at}", styles["subtitle"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=_PRIMARY))
    story.append(Spacer(1, 0.4 * cm))

    if summary:
        story.append(Paragraph("Overall Performance Summary", styles["section"]))
        overall_score = float(summary.get("overall_score", 0))
        readiness = summary.get("readiness", "N/A")

        summary_data = [
            ["Overall Score", f"{overall_score:.0f} / 100"],
            ["Readiness Level", readiness],
            ["Total Questions", str(len(questions))],
            ["Answered", str(sum(1 for a in answers if a and a.strip()))],
        ]
        tbl = Table(summary_data, colWidths=[5 * cm, 10 * cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), _BG),
            ("TEXTCOLOR", (0, 0), (0, -1), _TEXT),
            ("TEXTCOLOR", (1, 0), (1, -1), _TEXT),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_SURFACE, _BG]),
            ("GRID", (0, 0), (-1, -1), 0.5, _BORDER),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.3 * cm))

        strong = summary.get("strong_areas") or []
        if strong:
            story.append(Paragraph("Strong Areas:", styles["label"]))
            for item in strong:
                story.append(Paragraph(f'&nbsp;&nbsp;<font color="{_SUCCESS.hexval()}">✓</font>  {item}', styles["body"]))

        weak = summary.get("weak_areas") or []
        if weak:
            story.append(Paragraph("Areas for Improvement:", styles["label"]))
            for item in weak:
                story.append(Paragraph(f'&nbsp;&nbsp;<font color="{_ERROR.hexval()}">✗</font>  {item}', styles["body"]))

        recs = summary.get("recommendations") or []
        if recs:
            story.append(Paragraph("Recommendations:", styles["label"]))
            for i, rec in enumerate(recs, 1):
                story.append(Paragraph(f'&nbsp;&nbsp;<font color="{_INFO.hexval()}">💡</font>  {i}. {rec}', styles["body"]))

        story.append(Spacer(1, 0.2 * cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=_BORDER))

    story.append(Paragraph("Detailed Question Analysis", styles["section"]))
    story.append(Spacer(1, 0.1 * cm))

    for i, q_obj in enumerate(questions):
        category = q_obj.get("category", "") if isinstance(q_obj, dict) else ""
        difficulty = q_obj.get("difficulty", "") if isinstance(q_obj, dict) else ""

        tag = f" [{category}]" if category else ""
        tag += f" [{difficulty}]" if difficulty else ""
        story.append(Paragraph(f"Question {i+1} Performance{tag}", styles["question"]))

        if i < len(evaluations) and evaluations[i].get("success"):
            ev = evaluations[i].get("data", {})
            score = ev.get("score", 0)
            verdict = ev.get("verdict", "")
            sc = _score_color(score)

            score_data = [["Score", f"{score}/10", "Verdict", verdict]]
            score_tbl = Table(score_data, colWidths=[2.5 * cm, 3 * cm, 2.5 * cm, 5 * cm])
            score_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), _BG),
                ("BACKGROUND", (2, 0), (2, 0), _BG),
                ("TEXTCOLOR", (1, 0), (1, 0), sc),
                ("TEXTCOLOR", (3, 0), (3, 0), _verdict_color(verdict)),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, _BORDER),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(score_tbl)
            story.append(Spacer(1, 0.1 * cm))

            strengths = ev.get("strengths") or []
            if strengths:
                story.append(Paragraph("Strengths:", styles["label"]))
                for s in strengths:
                    story.append(Paragraph(f'&nbsp;&nbsp;<font color="{_SUCCESS.hexval()}">✓</font> {s}', styles["body"]))

            missing = ev.get("missing_concepts") or []
            if missing:
                story.append(Paragraph("Missing Concepts:", styles["label"]))
                for m in missing:
                    story.append(Paragraph(f'&nbsp;&nbsp;<font color="{_ERROR.hexval()}">✗</font> {m}', styles["body"]))

            suggestions = ev.get("improvement_suggestions") or []
            if suggestions:
                story.append(Paragraph("Improvement Tips:", styles["label"]))
                for tip in suggestions:
                    story.append(Paragraph(f'&nbsp;&nbsp;<font color="{_WARNING.hexval()}">➜</font> {tip}', styles["body"]))

        story.append(Spacer(1, 0.15 * cm))
        story.append(HRFlowable(width="100%", thickness=0.3, color=_BORDER))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def get_pdf_filename(meta: Optional[dict[str, Any]] = None) -> str:
    dt = datetime.now().strftime("%Y%m%d_%H%M")
    title = (meta or {}).get("title", "interview")
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in (title or "interview"))
    return f"interview_report_{safe_title}_{dt}.pdf"
