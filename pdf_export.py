"""
pdf_export.py
--------------
Generates a downloadable PDF report summarizing all generated business
ideas, using reportlab (pure Python, no external binaries required --
safe for Streamlit Cloud deployment).
"""

from io import BytesIO
from datetime import datetime
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from idea_generator import BusinessIdea


# --------------------------------------------------------------------------
# Style setup
# --------------------------------------------------------------------------

def _build_styles():
    """Create and return a dict of paragraph styles used in the PDF."""
    base_styles = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "TitleCustom",
            parent=base_styles["Title"],
            fontSize=22,
            textColor=colors.HexColor("#6C5CE7"),
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCustom",
            parent=base_styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#636E72"),
            alignment=TA_CENTER,
            spaceAfter=20,
        ),
        "idea_title": ParagraphStyle(
            "IdeaTitle",
            parent=base_styles["Heading1"],
            fontSize=16,
            textColor=colors.HexColor("#2D3436"),
            spaceAfter=4,
        ),
        "section_heading": ParagraphStyle(
            "SectionHeading",
            parent=base_styles["Heading3"],
            fontSize=11.5,
            textColor=colors.HexColor("#6C5CE7"),
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "BodyCustom",
            parent=base_styles["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#2D3436"),
        ),
        "bullet": ParagraphStyle(
            "BulletCustom",
            parent=base_styles["Normal"],
            fontSize=10,
            leading=14,
            leftIndent=12,
            bulletIndent=0,
            textColor=colors.HexColor("#2D3436"),
        ),
        "footer": ParagraphStyle(
            "FooterCustom",
            parent=base_styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#B2BEC3"),
            alignment=TA_CENTER,
        ),
    }
    return styles


def _score_color(score: int) -> colors.Color:
    """Return a color representing the score quality (red -> amber -> green)."""
    if score >= 75:
        return colors.HexColor("#00B894")
    elif score >= 50:
        return colors.HexColor("#FDCB6E")
    else:
        return colors.HexColor("#FF7675")


# --------------------------------------------------------------------------
# Main PDF builder
# --------------------------------------------------------------------------

def generate_pdf_report(
    ideas: List[BusinessIdea],
    budget: float,
    location: str,
    category: str,
    experience: str,
    weekly_hours: int,
) -> bytes:
    """Build a complete PDF report for the generated business ideas.

    Returns
    -------
    bytes
        The PDF file content, ready to be served via st.download_button.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        title="AI Business Idea Generator Report",
    )
    styles = _build_styles()
    story = []

    # ---- Cover / header section -----------------------------------------
    story.append(Paragraph("AI Business Idea Generator", styles["title"]))
    story.append(Paragraph("Personalized Business Idea Report", styles["subtitle"]))

    generated_on = datetime.now().strftime("%B %d, %Y at %H:%M")
    summary_data = [
        ["Budget", f"${budget:,.0f}"],
        ["Location", Paragraph(location or "N/A", styles["body"])],
        ["Area of Interest", category],
        ["Experience Level", experience],
        ["Time Available", f"{weekly_hours} hrs/week"],
        ["Generated On", generated_on],
    ]
    summary_table = Table(summary_data, colWidths=[5 * cm, 9 * cm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F0FB")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#6C5CE7")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DFE6E9")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 16))
    story.append(
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DFE6E9"))
    )
    story.append(Spacer(1, 10))

    # ---- One section per idea ---------------------------------------------
    for idea in ideas:
        story.append(Spacer(1, 6))

        # Title row: rank + name + score badge (as a small table for layout).
        title_para = Paragraph(
            f"#{idea.rank} &nbsp;&nbsp; {idea.name}", styles["idea_title"]
        )
        score_hex = "#" + _score_color(idea.score).hexval()[2:]
        score_para = Paragraph(
            f'<font color="{score_hex}">'
            f"<b>Score: {idea.score}/100</b></font>",
            styles["body"],
        )
        header_table = Table([[title_para, score_para]], colWidths=[12.5 * cm, 3.5 * cm])
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        story.append(header_table)
        story.append(Paragraph(idea.description, styles["body"]))
        story.append(Spacer(1, 6))

        # Key facts table. Long text values are wrapped in Paragraph objects
        # so they wrap within the cell instead of overflowing the page.
        cell_style = styles["body"]
        facts_data = [
            [
                "Startup Cost",
                Paragraph(
                    f"${idea.startup_cost_min:,.0f} - ${idea.startup_cost_max:,.0f}",
                    cell_style,
                ),
                "Difficulty",
                Paragraph(idea.difficulty, cell_style),
            ],
            [
                "Monthly Income",
                Paragraph(
                    f"${idea.monthly_income_min:,.0f} - ${idea.monthly_income_max:,.0f}",
                    cell_style,
                ),
                "Target Customers",
                Paragraph(idea.target_customers, cell_style),
            ],
        ]
        facts_table = Table(facts_data, colWidths=[3.0 * cm, 3.8 * cm, 3.0 * cm, 6.0 * cm])
        facts_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#6C5CE7")),
                    ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#6C5CE7")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DFE6E9")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(facts_table)
        story.append(Spacer(1, 6))

        # Revenue model.
        story.append(Paragraph("Revenue Model", styles["section_heading"]))
        story.append(Paragraph(idea.revenue_model, styles["body"]))

        # Advantages / risks as a two-column table for compactness.
        adv_text = "<br/>".join([f"&bull; {a}" for a in idea.advantages])
        risk_text = "<br/>".join([f"&bull; {r}" for r in idea.risks])
        adv_risk_table = Table(
            [
                [
                    Paragraph("<b>Advantages</b><br/>" + adv_text, styles["body"]),
                    Paragraph("<b>Risks</b><br/>" + risk_text, styles["body"]),
                ]
            ],
            colWidths=[8 * cm, 8 * cm],
        )
        adv_risk_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (1, 0), (1, 0), 0),
                    ("RIGHTPADDING", (0, 0), (0, 0), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(adv_risk_table)
        story.append(Spacer(1, 6))

        # First steps.
        story.append(Paragraph("First 5 Steps to Start", styles["section_heading"]))
        for i, step in enumerate(idea.first_steps, start=1):
            story.append(Paragraph(f"{i}. {step}", styles["bullet"]))

        story.append(Spacer(1, 14))
        story.append(
            HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#DFE6E9"))
        )

        # Page break after each idea except the last one, to keep ideas readable.
        if idea.rank != len(ideas):
            story.append(PageBreak())

    # ---- Footer note on the last page --------------------------------------
    story.append(Spacer(1, 16))
    story.append(
        Paragraph(
            "Generated by AI Business Idea Generator. Figures are estimates "
            "for planning purposes only and are not a guarantee of financial "
            "outcomes. Always conduct your own market research before "
            "investing.",
            styles["footer"],
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
