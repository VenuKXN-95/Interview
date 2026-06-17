"""
ReportLab PDF builder — constructs the interview report PDF.
Sections:
  1. Header (branding + candidate info)
  2. Score Summary (visual score bars)
  3. Recommendation
  4. Per-Question Breakdown (question → answer → evaluation)
  5. Session Feedback (strengths, improvements, next steps)
  6. Footer
"""
import os
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Color palette
C_BRAND = colors.HexColor("#1a1a2e")
C_ACCENT = colors.HexColor("#4f8ef7")
C_SUCCESS = colors.HexColor("#22c55e")
C_WARNING = colors.HexColor("#f59e0b")
C_DANGER = colors.HexColor("#ef4444")
C_LIGHT = colors.HexColor("#f8fafc")
C_TEXT = colors.HexColor("#1e293b")
C_MUTED = colors.HexColor("#64748b")

_RECOMMENDATION_COLORS = {
    "strong_hire": C_SUCCESS,
    "hire": colors.HexColor("#3b82f6"),
    "maybe": C_WARNING,
    "no_hire": C_DANGER,
}
_RECOMMENDATION_LABELS = {
    "strong_hire": "✓ STRONG HIRE",
    "hire": "✓ HIRE",
    "maybe": "~ MAYBE",
    "no_hire": "✗ NO HIRE",
}


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontSize=22,
            textColor=C_BRAND,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontSize=12,
            textColor=C_MUTED,
            spaceAfter=4,
        ),
        "section_header": ParagraphStyle(
            "section_header",
            parent=base["Heading2"],
            fontSize=14,
            textColor=C_BRAND,
            spaceBefore=12,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        ),
        "question": ParagraphStyle(
            "question",
            parent=base["Normal"],
            fontSize=10,
            textColor=C_TEXT,
            fontName="Helvetica-Bold",
            spaceAfter=3,
        ),
        "answer": ParagraphStyle(
            "answer",
            parent=base["Normal"],
            fontSize=9,
            textColor=C_TEXT,
            leftIndent=10,
            spaceAfter=3,
        ),
        "label": ParagraphStyle(
            "label",
            parent=base["Normal"],
            fontSize=9,
            textColor=C_MUTED,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontSize=9,
            textColor=C_TEXT,
            spaceAfter=3,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontSize=9,
            textColor=C_TEXT,
            leftIndent=12,
            bulletIndent=2,
        ),
        "recommendation": ParagraphStyle(
            "recommendation",
            parent=base["Normal"],
            fontSize=18,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        ),
    }


def build_report_pdf(
    output_path: str,
    report_data: dict,
) -> str:
    """
    Build the PDF interview report and write to output_path.
    Returns the output_path.

    report_data keys:
      candidate_name, interview_type, generated_at, scores (dict),
      recommendation, questions_and_answers (list), session_feedback (dict)
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Interview Report — {report_data.get('candidate_name', 'Candidate')}",
        author="Mock Interview Platform",
    )

    S = _styles()
    story = []

    # ── 1. Header ────────────────────────────────────────────
    story.append(Paragraph("Mock Interview Platform", S["title"]))
    story.append(Paragraph("AI-Powered Interview Assessment Report", S["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=C_ACCENT))
    story.append(Spacer(1, 0.3 * cm))

    info_data = [
        ["Candidate:", report_data.get("candidate_name", "N/A"),
         "Interview Type:", report_data.get("interview_type", "").upper()],
        ["Date:", report_data.get("generated_at", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")),
         "Total Questions:", str(report_data.get("total_questions", 0))],
        ["Answered:", str(report_data.get("answered_questions", 0)),
         "Status:", "Completed"],
    ]
    info_table = Table(info_data, colWidths=[3 * cm, 6 * cm, 3.5 * cm, 4.5 * cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, -1), C_TEXT),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_LIGHT, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.4 * cm))

    # ── 2. Score Summary ─────────────────────────────────────
    story.append(Paragraph("Score Summary", S["section_header"]))
    scores = report_data.get("scores", {})
    score_rows = [
        ["Dimension", "Score", "Visual"],
        ["Technical Knowledge", f"{scores.get('technical_score', 0):.1f}/10", _score_bar(scores.get('technical_score', 0))],
        ["Communication", f"{scores.get('communication_score', 0):.1f}/10", _score_bar(scores.get('communication_score', 0))],
        ["Problem Solving", f"{scores.get('problem_solving_score', 0):.1f}/10", _score_bar(scores.get('problem_solving_score', 0))],
        ["Project Understanding", f"{scores.get('project_score', 0):.1f}/10", _score_bar(scores.get('project_score', 0))],
        ["OVERALL SCORE", f"{scores.get('overall_score', 0):.1f}/10", _score_bar(scores.get('overall_score', 0), bold=True)],
    ]
    score_table = Table(score_rows, colWidths=[6 * cm, 2.5 * cm, 8.5 * cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f0fe")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [C_LIGHT, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── 3. Recommendation ────────────────────────────────────
    rec = report_data.get("recommendation", "maybe")
    rec_color = _RECOMMENDATION_COLORS.get(rec, C_WARNING)
    rec_label = _RECOMMENDATION_LABELS.get(rec, rec.upper())
    rec_table = Table([[Paragraph(rec_label, S["recommendation"])]],
                      colWidths=[17 * cm])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), rec_color),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("PADDING", (0, 0), (0, 0), 14),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 0.6 * cm))

    # ── 4. Session Feedback ───────────────────────────────────
    sf = report_data.get("session_feedback", {})
    if sf:
        story.append(Paragraph("Overall Interview Feedback", S["section_header"]))
        if sf.get("overall_assessment"):
            story.append(Paragraph(sf["overall_assessment"], S["body"]))
            story.append(Spacer(1, 0.2 * cm))

        if sf.get("key_strengths"):
            story.append(Paragraph("Key Strengths", S["label"]))
            for s in sf["key_strengths"]:
                story.append(Paragraph(f"• {s}", S["bullet"]))
            story.append(Spacer(1, 0.2 * cm))

        if sf.get("priority_improvements"):
            story.append(Paragraph("Priority Improvements", S["label"]))
            for imp in sf["priority_improvements"]:
                story.append(Paragraph(f"• {imp}", S["bullet"]))
            story.append(Spacer(1, 0.2 * cm))

        if sf.get("next_steps"):
            story.append(Paragraph("Recommended Next Steps", S["label"]))
            for step in sf["next_steps"]:
                story.append(Paragraph(f"→ {step}", S["bullet"]))
            story.append(Spacer(1, 0.4 * cm))

    # ── 5. Per-Question Breakdown ─────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Detailed Question & Answer Breakdown", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_ACCENT))
    story.append(Spacer(1, 0.3 * cm))

    qa_list = report_data.get("questions_and_answers", [])
    for i, qa in enumerate(qa_list, 1):
        score_val = qa.get("score", 0)
        score_color = (
            C_SUCCESS if score_val >= 7
            else C_WARNING if score_val >= 5
            else C_DANGER
        )
        header_data = [[
            Paragraph(f"Q{i}. {qa.get('question', '')}", S["question"]),
            Paragraph(f"Score: {score_val:.1f}/10", ParagraphStyle(
                "score_cell", parent=S["label"],
                textColor=score_color, alignment=TA_RIGHT
            )),
        ]]
        header_table = Table(header_data, colWidths=[13 * cm, 4 * cm])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))

        answer_text = qa.get("answer", "") or "[No answer provided]"
        blocks = [
            header_table,
            Spacer(1, 0.15 * cm),
            Paragraph("<b>Answer:</b>", S["label"]),
            Paragraph(answer_text[:800], S["answer"]),
            Spacer(1, 0.1 * cm),
        ]

        eval_data = qa.get("evaluation", {})
        if eval_data.get("strengths"):
            blocks.append(Paragraph("<b>Strengths:</b>", S["label"]))
            for s in eval_data["strengths"][:2]:
                blocks.append(Paragraph(f"✓ {s}", S["bullet"]))
        if eval_data.get("weaknesses"):
            blocks.append(Paragraph("<b>Areas to Improve:</b>", S["label"]))
            for w in eval_data["weaknesses"][:2]:
                blocks.append(Paragraph(f"△ {w}", S["bullet"]))
        if eval_data.get("feedback", {}).get("recommendations"):
            blocks.append(Paragraph("<b>Recommendations:</b>", S["label"]))
            for r in eval_data["feedback"]["recommendations"][:2]:
                blocks.append(Paragraph(f"→ {r}", S["bullet"]))

        blocks.append(Spacer(1, 0.3 * cm))
        story.append(KeepTogether(blocks))

    # ── 6. Footer text ────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=C_MUTED))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"Generated by Mock Interview Platform | {datetime.utcnow().strftime('%Y-%m-%d')} | Confidential",
        ParagraphStyle("footer", parent=S["body"], textColor=C_MUTED, alignment=TA_CENTER, fontSize=8),
    ))

    doc.build(story)
    return output_path


def _score_bar(score: float, bold: bool = False) -> str:
    """Create a text-based score bar for ReportLab tables."""
    filled = round((score / 10) * 20)
    empty = 20 - filled
    bar = "█" * filled + "░" * empty
    return f"{bar} {score:.1f}"
