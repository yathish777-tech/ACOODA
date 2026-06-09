import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'college_logo.png')

STATUS_COLORS = {
    'HOD Approved': colors.HexColor('#16a34a'),
    'Pending Tutor Review': colors.HexColor('#d97706'),
    'Pending HOD Review': colors.HexColor('#2563eb'),
    'Tutor Approved': colors.HexColor('#7c3aed'),
    'Tutor Rejected': colors.HexColor('#dc2626'),
    'HOD Rejected': colors.HexColor('#dc2626'),
}

def generate_od_pdf(application, student):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', prefix='OD_')
    tmp.close()

    doc = SimpleDocTemplate(
        tmp.name,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header ──────────────────────────────────────────────────
    college_blue = colors.HexColor('#1e3a5f')
    gold = colors.HexColor('#c9a84c')

    header_data = [['', '', '']]
    if os.path.exists(LOGO_PATH):
        logo = RLImage(LOGO_PATH, width=1.8*cm, height=1.8*cm)
        header_data[0][0] = logo

    college_name = Paragraph(
        '<font size="14" color="#1e3a5f"><b>ADHIYAMAAN COLLEGE OF ENGINEERING</b></font><br/>'
        '<font size="9" color="#555555">Hosur - 635 109, Krishnagiri Dt., Tamil Nadu</font><br/>'
        '<font size="9" color="#555555">Autonomous Institution | Affiliated to Anna University</font>',
        ParagraphStyle('ch', alignment=TA_CENTER, spaceAfter=0)
    )
    acooda_title = Paragraph(
        '<font size="11" color="#c9a84c"><b>ACOODA</b></font><br/>'
        '<font size="7" color="#888">On-Duty Portal</font>',
        ParagraphStyle('ac', alignment=TA_RIGHT, spaceAfter=0)
    )
    header_data[0] = [logo if os.path.exists(LOGO_PATH) else '', college_name, acooda_title]
    
    header_table = Table(header_data, colWidths=[2*cm, 12*cm, 3*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width='100%', thickness=2, color=college_blue, spaceAfter=4))
    story.append(HRFlowable(width='100%', thickness=1, color=gold, spaceAfter=8))

    # ── Title ────────────────────────────────────────────────────
    title_style = ParagraphStyle('title', fontSize=13, fontName='Helvetica-Bold',
                                  textColor=college_blue, alignment=TA_CENTER, spaceAfter=8)
    story.append(Paragraph('ON-DUTY PERMISSION LETTER', title_style))

    # ── Application ID & Date ────────────────────────────────────
    meta_style = ParagraphStyle('meta', fontSize=9, textColor=colors.HexColor('#555'))
    meta_data = [
        [Paragraph(f'<b>Application ID:</b> {application.application_id}', meta_style),
         Paragraph(f'<b>Date:</b> {application.created_at.strftime("%d-%m-%Y")}', meta_style)]
    ]
    meta_table = Table(meta_data, colWidths=[8.5*cm, 8.5*cm])
    story.append(meta_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Student Details ──────────────────────────────────────────
    section_style = ParagraphStyle('section', fontSize=10, fontName='Helvetica-Bold',
                                    textColor=college_blue, spaceBefore=8, spaceAfter=4)
    story.append(Paragraph('Student Information', section_style))
    story.append(HRFlowable(width='100%', thickness=0.5, color=gold, spaceAfter=6))

    cell_style = ParagraphStyle('cell', fontSize=9)
    label_style = ParagraphStyle('label', fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor('#1e3a5f'))

    student_data = [
        [Paragraph('Register Number', label_style), Paragraph(str(student.register_no), cell_style),
         Paragraph('Name', label_style), Paragraph(student.name, cell_style)],
        [Paragraph('Department', label_style), Paragraph(student.department, cell_style),
         Paragraph('Year & Section', label_style), Paragraph(f'{student.year} Year - Section {student.section}', cell_style)],
        [Paragraph('Email', label_style), Paragraph(student.email, cell_style),
         Paragraph('', label_style), Paragraph('', cell_style)],
    ]
    student_table = Table(student_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 4*cm])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8faff')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f0f4ff'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#d0d8e8')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(student_table)
    story.append(Spacer(1, 0.3*cm))

    # ── Event Details ────────────────────────────────────────────
    story.append(Paragraph('Event Details', section_style))
    story.append(HRFlowable(width='100%', thickness=0.5, color=gold, spaceAfter=6))

    event_data = [
        [Paragraph('Event Name', label_style), Paragraph(application.event_name, cell_style),
         Paragraph('Category', label_style), Paragraph(application.reason, cell_style)],
        [Paragraph('Event Date', label_style), Paragraph(application.event_date.strftime('%d-%m-%Y'), cell_style),
         Paragraph('Dates of OD', label_style), Paragraph(f'{application.from_date.strftime("%d-%m-%Y")} to {application.to_date.strftime("%d-%m-%Y")}', cell_style)],
    ]
    event_table = Table(event_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 4*cm])
    event_table.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f0f4ff'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#d0d8e8')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(event_table)

    # ── Description ──────────────────────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Reason / Description', section_style))
    story.append(HRFlowable(width='100%', thickness=0.5, color=gold, spaceAfter=4))
    desc_style = ParagraphStyle('desc', fontSize=9, leading=14, leftIndent=0.3*cm,
                                 borderPad=6, backColor=colors.HexColor('#f8f9fa'),
                                 borderColor=colors.HexColor('#d0d8e8'), borderWidth=0.3)
    story.append(Paragraph(application.description, desc_style))

    # ── Status ───────────────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph('Approval Status', section_style))
    story.append(HRFlowable(width='100%', thickness=0.5, color=gold, spaceAfter=6))

    status_color = STATUS_COLORS.get(application.status, colors.HexColor('#374151'))
    status_style = ParagraphStyle('status', fontSize=11, fontName='Helvetica-Bold',
                                   textColor=status_color, alignment=TA_CENTER)
    story.append(Paragraph(f'● {application.status.upper()}', status_style))

    if application.tutor_remark:
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(f'<b>Tutor Remark:</b> {application.tutor_remark}',
                                ParagraphStyle('remark', fontSize=9, textColor=colors.HexColor('#555'))))
    if application.hod_remark:
        story.append(Paragraph(f'<b>HOD Remark:</b> {application.hod_remark}',
                                ParagraphStyle('remark2', fontSize=9, textColor=colors.HexColor('#555'))))

    # ── Approval Information ─────────────────────────────────────
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph('Approval Information', section_style))
    story.append(HRFlowable(width='100%', thickness=0.5, color=gold, spaceAfter=6))

    approval_data = [
        [Paragraph('Student Name', label_style), Paragraph(student.name, cell_style),
         Paragraph('Tutor Assigned', label_style), Paragraph(application.tutor.tutor_name if application.tutor else 'N/A', cell_style)],
        [Paragraph('Current Status', label_style), 
         Paragraph(f'<font color="{status_color.hexval()}">{application.status}</font>', cell_style),
         Paragraph('HOD Assigned', label_style), Paragraph(application.hod.hod_name if application.hod else 'N/A', cell_style)],
        [Paragraph('Submission Date', label_style), 
         Paragraph(application.created_at.strftime('%d-%m-%Y %H:%M'), cell_style),
         Paragraph('Last Updated', label_style), 
         Paragraph((application.hod_reviewed_at or application.tutor_reviewed_at or application.created_at).strftime('%d-%m-%Y %H:%M'), cell_style)],
    ]
    approval_table = Table(approval_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 4*cm])
    approval_table.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f0f4ff'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#d0d8e8')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(approval_table)

    # ── Tutor Review Information ─────────────────────────────────
    if application.tutor:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph('Tutor Review Information', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=gold, spaceAfter=6))

        tutor_status = 'Pending' if application.tutor_reviewed_at is None else ('Approved' if 'Approved' in application.status else 'Rejected' if 'Rejected' in application.status else 'Forwarded')
        tutor_data = [
            [Paragraph('Tutor Name', label_style), Paragraph(application.tutor.tutor_name, cell_style),
             Paragraph('Tutor Status', label_style), Paragraph(tutor_status, cell_style)],
            [Paragraph('Review Date', label_style), 
             Paragraph(application.tutor_reviewed_at.strftime('%d-%m-%Y %H:%M') if application.tutor_reviewed_at else 'Pending', cell_style),
             Paragraph('Tutor Email', label_style), Paragraph(application.tutor.email, cell_style)],
        ]
        tutor_table = Table(tutor_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 4*cm])
        tutor_table.setStyle(TableStyle([
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f0f4ff'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#d0d8e8')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(tutor_table)

        if application.tutor_remark:
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(f'<b>Tutor Remarks:</b> {application.tutor_remark}',
                                    ParagraphStyle('tutor_remark', fontSize=8, textColor=colors.HexColor('#555'), leading=12)))

    # ── HOD Review Information ───────────────────────────────────
    if application.hod:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph('HOD Review Information', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=gold, spaceAfter=6))

        hod_status = 'Pending' if application.hod_reviewed_at is None else ('Approved' if 'Approved' in application.status else 'Rejected' if 'Rejected' in application.status else 'Under Review')
        hod_data = [
            [Paragraph('HOD Name', label_style), Paragraph(application.hod.hod_name, cell_style),
             Paragraph('HOD Status', label_style), Paragraph(hod_status, cell_style)],
            [Paragraph('Review Date', label_style), 
             Paragraph(application.hod_reviewed_at.strftime('%d-%m-%Y %H:%M') if application.hod_reviewed_at else 'Pending', cell_style),
             Paragraph('HOD Email', label_style), Paragraph(application.hod.email, cell_style)],
        ]
        hod_table = Table(hod_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 4*cm])
        hod_table.setStyle(TableStyle([
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f0f4ff'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#d0d8e8')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(hod_table)

        if application.hod_remark:
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(f'<b>HOD Remarks:</b> {application.hod_remark}',
                                    ParagraphStyle('hod_remark', fontSize=8, textColor=colors.HexColor('#555'), leading=12)))

    # ── Footer ───────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=gold, spaceAfter=4))
    footer_style = ParagraphStyle('footer', fontSize=7, textColor=colors.HexColor('#999'), alignment=TA_CENTER)
    story.append(Paragraph(
        f'Generated by ACOODA - Adhiyamaan College Online On-Duty Application System | {datetime.now().strftime("%d-%m-%Y %H:%M")}',
        footer_style))

    doc.build(story)
    return tmp.name
