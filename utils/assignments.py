import re

from models import db, Application, HOD, Student, Tutor


DEPARTMENT_ALIASES = {
    'cse': 'computerscienceandengineering',
    'cs': 'computerscienceandengineering',
    'it': 'informationtechnology',
    'ece': 'electronicsandcommunicationengineering',
    'eee': 'electricalandelectronicsengineering',
    'mech': 'mechanicalengineering',
    'mechanical': 'mechanicalengineering',
    'civil': 'civilengineering',
    'aiads': 'artificialintelligenceanddatascience',
    'aids': 'artificialintelligenceanddatascience',
}


def normalize_section(value):
    section = str(value or '').strip().lower().replace('section', '')
    return re.sub(r'[^a-z0-9]', '', section).upper()


def normalize_department(value):
    department = re.sub(r'[^a-z0-9]', '', str(value or '').strip().lower())
    for short_name, canonical in DEPARTMENT_ALIASES.items():
        if department == short_name or department.startswith(short_name):
            return canonical
    return DEPARTMENT_ALIASES.get(department, department)


def department_matches(left, right):
    left_norm = normalize_department(left)
    right_norm = normalize_department(right)
    if not left_norm or not right_norm:
        return False
    return left_norm == right_norm or left_norm in right_norm or right_norm in left_norm


def find_tutor_for_student(student):
    student_section = normalize_section(student.section)
    candidates = Tutor.query.filter_by(
        year_handling=student.year,
        is_active=True
    ).order_by(Tutor.id.asc()).all()

    section_matches = [
        tutor for tutor in candidates
        if normalize_section(tutor.section_handling) == student_section
    ]
    if not section_matches:
        return None

    for tutor in section_matches:
        if department_matches(student.department, tutor.department):
            return tutor

    return section_matches[0]


def find_hod_for_student(student):
    hods = HOD.query.filter_by(is_active=True).order_by(HOD.id.asc()).all()
    for hod in hods:
        if department_matches(student.department, hod.department):
            return hod
    return None


def assign_application_staff(application, student=None):
    student = student or db.session.get(Student, application.student_id)
    if not student:
        return None, None

    tutor = find_tutor_for_student(student)
    hod = find_hod_for_student(student)

    if tutor:
        application.tutor_id = tutor.id
        application.tutor_name = tutor.tutor_name
    if hod:
        application.hod_id = hod.id

    return tutor, hod


def backfill_unassigned_applications_for_tutor(tutor):
    applications = (
        Application.query
        .join(Student, Application.student_id == Student.id)
        .filter(Application.tutor_id.is_(None))
        .filter(Student.year == tutor.year_handling)
        .all()
    )

    updated = []
    for application in applications:
        assigned_tutor, _ = assign_application_staff(application, application.student)
        if assigned_tutor and assigned_tutor.id == tutor.id:
            updated.append(application)

    return updated
