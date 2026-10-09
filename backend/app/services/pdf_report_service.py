from html import escape
from io import BytesIO
from urllib.parse import urlsplit

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.schemas import InvestigationReport


GREEN = colors.HexColor("#11683C")
MINT = colors.HexColor("#EFFAF4")
INK = colors.HexColor("#173B2A")
MUTED = colors.HexColor("#526F5E")
LINE = colors.HexColor("#D8EBE0")


def _safe_link(url: str | None, label: str) -> str:
    if not url:
        return escape(label)
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return escape(label)
    return f'<link href="{escape(url, quote=True)}" color="#11683C"><u>{escape(label)}</u></link>'


def _bullet(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(f'<font color="#16834B">&#8226;</font> {escape(text)}', style)


def build_investigation_pdf(report: InvestigationReport) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=19 * mm,
        leftMargin=19 * mm,
        topMargin=24 * mm,
        bottomMargin=20 * mm,
        title=f"RepoXray Report - {report.issue.owner}/{report.issue.repository} #{report.issue.number}",
        author="RepoXray",
        pageCompression=0,
    )

    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=28,
            textColor=GREEN,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            fontSize=10,
            leading=15,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=16,
        ),
        "section": ParagraphStyle(
            "ReportSection",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=GREEN,
            spaceBefore=15,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "item": ParagraphStyle(
            "ReportItem",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=INK,
            spaceBefore=5,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=base["BodyText"],
            fontSize=9,
            leading=13,
            textColor=INK,
            spaceAfter=5,
            wordWrap="CJK",
        ),
        "small": ParagraphStyle(
            "ReportSmall",
            parent=base["BodyText"],
            fontSize=8,
            leading=11,
            textColor=MUTED,
            spaceAfter=4,
            wordWrap="CJK",
        ),
        "callout": ParagraphStyle(
            "ReportCallout",
            parent=base["BodyText"],
            fontSize=10,
            leading=15,
            textColor=INK,
            backColor=MINT,
            borderColor=LINE,
            borderWidth=0.7,
            borderPadding=9,
            spaceAfter=6,
            wordWrap="CJK",
        ),
        "label": ParagraphStyle(
            "ReportLabel",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=GREEN,
        ),
    }

    def draw_page(canvas, doc) -> None:
        canvas.saveState()
        width, height = A4
        canvas.setFillColor(GREEN)
        canvas.rect(0, height - 7 * mm, width, 7 * mm, stroke=0, fill=1)
        canvas.setStrokeColor(LINE)
        canvas.line(19 * mm, 15 * mm, width - 19 * mm, 15 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(19 * mm, 10 * mm, "RepoXray | Evidence-based investigation report")
        canvas.drawRightString(width - 19 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    story = [
        Spacer(1, 5 * mm),
        Paragraph("RepoXray", styles["title"]),
        Paragraph("GitHub Issue Investigation Report", styles["subtitle"]),
        HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=12),
        Paragraph(escape(report.issue.title or "Untitled GitHub issue"), styles["section"]),
    ]

    issue_rows = [
        [Paragraph("Repository", styles["label"]), Paragraph(escape(f"{report.issue.owner}/{report.issue.repository}"), styles["body"])],
        [Paragraph("Issue", styles["label"]), Paragraph(_safe_link(report.issue.url, f"#{report.issue.number}"), styles["body"])],
        [Paragraph("State", styles["label"]), Paragraph(escape(report.issue.state.title()), styles["body"])],
        [Paragraph("Report generated", styles["label"]), Paragraph(escape(report.created_at), styles["body"])],
    ]
    if report.issue.labels:
        issue_rows.append([Paragraph("Labels", styles["label"]), Paragraph(escape(", ".join(report.issue.labels)), styles["body"])])
    if report.issue.assignee:
        issue_rows.append([Paragraph("Assignee", styles["label"]), Paragraph(escape(report.issue.assignee), styles["body"])])

    issue_table = Table(issue_rows, colWidths=[34 * mm, 135 * mm], hAlign="LEFT")
    issue_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MINT),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.extend([issue_table, Paragraph("Executive summary", styles["section"])])
    story.append(Paragraph(escape(report.summary or "No executive summary was recorded."), styles["callout"]))
    if report.issue.body:
        story.extend([
            Paragraph("Issue description", styles["section"]),
            Paragraph(escape(report.issue.body).replace("\n", "<br/>"), styles["body"]),
        ])

    story.append(Paragraph("Candidate source files", styles["section"]))
    if report.relevant_files:
        story.append(Paragraph(
            "These are investigation candidates, not a claim that every file must change. Evidence labels are preserved from the investigation.",
            styles["small"],
        ))
        for item in report.relevant_files:
            story.append(Paragraph(_safe_link(item.url, item.path) if item.url else escape(item.path), styles["item"]))
            story.append(Paragraph(f"Evidence type: <b>{escape(item.evidence_type)}</b>", styles["small"]))
            story.append(Paragraph(escape(item.reason), styles["body"]))
            if item.line_start is not None:
                line_text = f"Lines {item.line_start}"
                if item.line_end is not None:
                    line_text += f"-{item.line_end}"
                story.append(Paragraph(escape(line_text), styles["small"]))
            if item.symbols:
                story.append(Paragraph(f"Symbols: {escape(', '.join(item.symbols))}", styles["small"]))
            if item.excerpt:
                story.append(Paragraph(f"<i>{escape(item.excerpt)}</i>", styles["small"]))
    else:
        story.append(Paragraph("No candidate source files were recorded.", styles["body"]))

    story.append(Paragraph("Relevant test candidates", styles["section"]))
    story.append(Paragraph(
        "Listed tests are candidates identified by the investigation. This report does not imply they were executed.",
        styles["small"],
    ))
    if report.relevant_tests:
        for item in report.relevant_tests:
            story.append(Paragraph(_safe_link(item.url, item.path) if item.url else escape(item.path), styles["item"]))
            story.append(Paragraph(
                f"Evidence type: <b>{escape(item.evidence_type)}</b> | Match type: {escape(item.match_type)}",
                styles["small"],
            ))
            story.append(Paragraph(escape(item.reason), styles["body"]))
            if item.test_functions:
                story.append(Paragraph(f"Test functions: {escape(', '.join(item.test_functions))}", styles["small"]))
            if item.excerpt:
                story.append(Paragraph(f"<i>{escape(item.excerpt)}</i>", styles["small"]))
    else:
        story.append(Paragraph("No relevant test candidates were recorded.", styles["body"]))

    story.append(Paragraph("Evidence and investigation trace", styles["section"]))
    trace_entries = [
        entry for entry in report.agent_trace
        if entry.result_summary or entry.error_message
    ]
    if trace_entries:
        for entry in trace_entries:
            story.append(Paragraph(
                f"Step {entry.step_number}: {escape(entry.action_description)}",
                styles["item"],
            ))
            if entry.result_summary:
                story.append(Paragraph(escape(entry.result_summary), styles["body"]))
            if entry.error_message:
                story.append(Paragraph(f"Recorded uncertainty/error: {escape(entry.error_message)}", styles["small"]))
    else:
        story.append(Paragraph("No investigation trace results were recorded.", styles["body"]))

    story.append(Paragraph("Possible conflicting or duplicate work", styles["section"]))
    if report.possible_conflicts:
        for conflict in report.possible_conflicts:
            story.append(Paragraph(
                f"{escape(conflict.title)} <font color='#526F5E'>[{escape(conflict.severity.upper())} | {escape(conflict.type)}]</font>",
                styles["item"],
            ))
            story.append(Paragraph(escape(conflict.description), styles["body"]))
            for link in conflict.linked_pr_urls:
                story.append(Paragraph(_safe_link(link, link), styles["small"]))
    else:
        story.append(Paragraph("No conflict findings were recorded by the investigation.", styles["body"]))

    story.append(Paragraph("Prioritized implementation roadmap", styles["section"]))
    story.append(Paragraph(
        "Steps retain the investigation's original order; lower step numbers are presented first as the reported priority. This plan is guidance, not executed work.",
        styles["small"],
    ))
    if report.contribution_steps:
        for step in sorted(report.contribution_steps, key=lambda item: item.step_number):
            story.append(Paragraph(
                f"Priority {step.step_number} | Step {step.step_number}: {escape(step.title)}",
                styles["item"],
            ))
            story.append(Paragraph(escape(step.description), styles["body"]))
            story.append(Paragraph(f"Action type: {escape(step.action_type)}", styles["small"]))
            if step.target_files:
                story.append(Paragraph(f"Target files: {escape(', '.join(step.target_files))}", styles["small"]))
            if step.test_command:
                story.append(Paragraph(
                    f"Suggested verification command (not run by this report): <font name='Courier'>{escape(step.test_command)}</font>",
                    styles["small"],
                ))
    else:
        story.append(Paragraph("No implementation roadmap steps were recorded.", styles["body"]))
    if report.contributing_command:
        story.append(Paragraph(
            f"Recorded contribution command (execution not verified): <font name='Courier'>{escape(report.contributing_command)}</font>",
            styles["small"],
        ))

    story.append(Paragraph("Warnings and limitations", styles["section"]))
    warnings = report.warnings + report.limitations
    if warnings:
        for warning in warnings:
            story.append(_bullet(warning, styles["body"]))
    else:
        story.append(Paragraph("No warnings or limitations were recorded by the investigation.", styles["body"]))

    story.append(Paragraph("Uncertainties", styles["section"]))
    if report.uncertainties:
        for uncertainty in report.uncertainties:
            story.append(_bullet(uncertainty, styles["body"]))
    else:
        story.append(Paragraph("No explicit uncertainties were recorded by the investigation.", styles["body"]))

    document.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    return buffer.getvalue()
