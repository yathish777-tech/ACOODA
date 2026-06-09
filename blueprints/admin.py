from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import login_required, current_user
from models import db, Student, Tutor, HOD, Application, AuditLog
from utils.assignments import normalize_section
import bcrypt, io, os
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def admin_log(action, remark=None):
    log = AuditLog(
        application_id='SYSTEM',
        action=action,
        performed_by=current_user.username,
        role='admin',
        remark=remark
    )
    db.session.add(log)

def hash_default_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def form_int(field_name):
    value = request.form.get(field_name, '').strip()
    return int(value) if value else None

def email_exists(model, email, current_id=None):
    query = model.query.filter(db.func.lower(model.email) == email.lower())
    if current_id:
        query = query.filter(model.id != current_id)
    return query.first() is not None

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'students': Student.query.count(),
        'tutors': Tutor.query.count(),
        'hods': HOD.query.count(),
        'applications': Application.query.count(),
        'pending': Application.query.filter(Application.status.like('%Pending%')).count(),
        'approved': Application.query.filter_by(status='HOD Approved').count(),
        'rejected': Application.query.filter(Application.status.like('%Rejected%')).count(),
    }
    recent_apps = Application.query.order_by(Application.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, recent_apps=recent_apps)

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin/students.html', students=students)

@admin_bp.route('/student/<int:sid>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_student(sid):
    student = Student.query.get_or_404(sid)
    student.is_active = not student.is_active
    status = 'activated' if student.is_active else 'deactivated'
    admin_log('Student Status Updated', f'{student.name} ({student.email}) {status}')
    db.session.commit()
    flash(f'Student {student.name} has been {status}.', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/tutors')
@login_required
@admin_required
def tutors():
    q = request.args.get('q', '').strip().lower()
    department = request.args.get('department', '').strip()
    year = request.args.get('year', '').strip()
    section = normalize_section(request.args.get('section', '').strip())

    all_tutors = Tutor.query.order_by(Tutor.created_at.desc()).all()
    tutors = all_tutors

    if q:
        tutors = [
            tutor for tutor in tutors
            if q in tutor.tutor_name.lower()
            or q in tutor.email.lower()
            or q in tutor.department.lower()
        ]
    if department:
        tutors = [tutor for tutor in tutors if tutor.department == department]
    if year:
        tutors = [tutor for tutor in tutors if str(tutor.year_handling) == year]
    if section:
        tutors = [tutor for tutor in tutors if normalize_section(tutor.section_handling) == section]

    filter_options = {
        'departments': sorted({t.department for t in all_tutors if t.department}),
        'years': sorted({t.year_handling for t in all_tutors if t.year_handling}),
        'sections': sorted({normalize_section(t.section_handling) for t in all_tutors if t.section_handling}),
    }
    return render_template('admin/tutors.html', tutors=tutors, filters={
        'q': request.args.get('q', '').strip(),
        'department': department,
        'year': year,
        'section': section,
    }, filter_options=filter_options)

@admin_bp.route('/tutor/add', methods=['POST'])
@login_required
@admin_required
def add_tutor():
    tutor_name = request.form.get('tutor_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    department = request.form.get('department', '').strip()
    year_handling = form_int('year_handling')
    section_handling = normalize_section(request.form.get('section_handling', ''))

    if not all([tutor_name, email, department, year_handling, section_handling]):
        flash('Please fill all tutor fields.', 'danger')
        return redirect(url_for('admin.tutors'))
    if email_exists(Tutor, email):
        flash('Tutor email already exists.', 'danger')
        return redirect(url_for('admin.tutors'))

    tutor = Tutor(
        tutor_name=tutor_name,
        email=email,
        department=department,
        year_handling=year_handling,
        section_handling=section_handling,
        password=hash_default_password('staff123'),
        must_change_password=True,
        is_active=True
    )
    db.session.add(tutor)
    admin_log('Tutor Added', f'{tutor_name} ({email})')
    db.session.commit()
    flash(f'Tutor {tutor_name} added successfully. Default password: staff123', 'success')
    return redirect(url_for('admin.tutors'))

@admin_bp.route('/tutor/<int:tid>/edit', methods=['POST'])
@login_required
@admin_required
def edit_tutor(tid):
    tutor = Tutor.query.get_or_404(tid)
    tutor_name = request.form.get('tutor_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    department = request.form.get('department', '').strip()
    year_handling = form_int('year_handling')
    section_handling = normalize_section(request.form.get('section_handling', ''))

    if not all([tutor_name, email, department, year_handling, section_handling]):
        flash('Please fill all tutor fields.', 'danger')
        return redirect(url_for('admin.tutors'))
    if email_exists(Tutor, email, current_id=tutor.id):
        flash('Tutor email already exists.', 'danger')
        return redirect(url_for('admin.tutors'))

    before = f'{tutor.tutor_name}, {tutor.email}, {tutor.department}, Year {tutor.year_handling}, Section {tutor.section_handling}'
    tutor.tutor_name = tutor_name
    tutor.email = email
    tutor.department = department
    tutor.year_handling = year_handling
    tutor.section_handling = section_handling
    Application.query.filter_by(tutor_id=tutor.id).update({'tutor_name': tutor_name})
    admin_log('Tutor Updated', f'{before} -> {tutor_name}, {email}, {department}, Year {year_handling}, Section {section_handling}')
    db.session.commit()
    flash(f'Tutor {tutor_name} updated successfully.', 'success')
    return redirect(url_for('admin.tutors'))

@admin_bp.route('/tutor/<int:tid>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tutor(tid):
    tutor = Tutor.query.get_or_404(tid)
    for application in Application.query.filter_by(tutor_id=tutor.id).all():
        application.tutor_name = application.tutor_name or tutor.tutor_name
        application.tutor_id = None
    admin_log('Tutor Deleted', f'{tutor.tutor_name} ({tutor.email})')
    db.session.delete(tutor)
    db.session.commit()
    flash(f'Tutor {tutor.tutor_name} deleted successfully.', 'success')
    return redirect(url_for('admin.tutors'))

@admin_bp.route('/hods')
@login_required
@admin_required
def hods():
    q = request.args.get('q', '').strip().lower()
    department = request.args.get('department', '').strip()

    all_hods = HOD.query.order_by(HOD.created_at.desc()).all()
    hods = all_hods

    if q:
        hods = [
            hod for hod in hods
            if q in hod.hod_name.lower()
            or q in hod.email.lower()
            or q in hod.department.lower()
        ]
    if department:
        hods = [hod for hod in hods if hod.department == department]

    filter_options = {
        'departments': sorted({h.department for h in all_hods if h.department}),
    }
    return render_template('admin/hods.html', hods=hods, filters={
        'q': request.args.get('q', '').strip(),
        'department': department,
    }, filter_options=filter_options)

@admin_bp.route('/hod/add', methods=['POST'])
@login_required
@admin_required
def add_hod():
    hod_name = request.form.get('hod_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    department = request.form.get('department', '').strip()

    if not all([hod_name, email, department]):
        flash('Please fill all HOD fields.', 'danger')
        return redirect(url_for('admin.hods'))
    if email_exists(HOD, email):
        flash('HOD email already exists.', 'danger')
        return redirect(url_for('admin.hods'))

    hod = HOD(
        hod_name=hod_name,
        email=email,
        department=department,
        password=hash_default_password('hod123'),
        must_change_password=True,
        is_active=True
    )
    db.session.add(hod)
    admin_log('HOD Added', f'{hod_name} ({email})')
    db.session.commit()
    flash(f'HOD {hod_name} added successfully. Default password: hod123', 'success')
    return redirect(url_for('admin.hods'))

@admin_bp.route('/hod/<int:hid>/edit', methods=['POST'])
@login_required
@admin_required
def edit_hod(hid):
    hod = HOD.query.get_or_404(hid)
    hod_name = request.form.get('hod_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    department = request.form.get('department', '').strip()

    if not all([hod_name, email, department]):
        flash('Please fill all HOD fields.', 'danger')
        return redirect(url_for('admin.hods'))
    if email_exists(HOD, email, current_id=hod.id):
        flash('HOD email already exists.', 'danger')
        return redirect(url_for('admin.hods'))

    before = f'{hod.hod_name}, {hod.email}, {hod.department}'
    hod.hod_name = hod_name
    hod.email = email
    hod.department = department
    admin_log('HOD Updated', f'{before} -> {hod_name}, {email}, {department}')
    db.session.commit()
    flash(f'HOD {hod_name} updated successfully.', 'success')
    return redirect(url_for('admin.hods'))

@admin_bp.route('/hod/<int:hid>/delete', methods=['POST'])
@login_required
@admin_required
def delete_hod(hid):
    hod = HOD.query.get_or_404(hid)
    Application.query.filter_by(hod_id=hod.id).update({'hod_id': None})
    admin_log('HOD Deleted', f'{hod.hod_name} ({hod.email})')
    db.session.delete(hod)
    db.session.commit()
    flash(f'HOD {hod.hod_name} deleted successfully.', 'success')
    return redirect(url_for('admin.hods'))

@admin_bp.route('/upload-tutors', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_tutors():
    if request.method == 'POST':
        file = request.files.get('excel_file')
        if not file or not file.filename.endswith(('.xlsx', '.xls')):
            flash('Please upload a valid Excel file.', 'danger')
            return redirect(url_for('admin.upload_tutors'))

        import pandas as pd
        try:
            df = pd.read_excel(file)
            required_cols = ['Tutor Name', 'Tutor Email', 'Department', 'Year Handling', 'Section Handling']
            if not all(col in df.columns for col in required_cols):
                flash(f'Excel must contain columns: {", ".join(required_cols)}', 'danger')
                return redirect(url_for('admin.upload_tutors'))

            added, skipped = 0, 0
            default_password = bcrypt.hashpw('staff123'.encode(), bcrypt.gensalt()).decode()
            for _, row in df.iterrows():
                email = str(row['Tutor Email']).strip().lower()
                if Tutor.query.filter_by(email=email).first():
                    skipped += 1
                    continue
                tutor = Tutor(
                    tutor_name=str(row['Tutor Name']).strip(),
                    email=email,
                    department=str(row['Department']).strip(),
                    year_handling=int(row['Year Handling']),
                    section_handling=normalize_section(row['Section Handling']),
                    password=default_password,
                    must_change_password=True
                )
                db.session.add(tutor)
                added += 1
            admin_log('Tutors Uploaded', f'{added} tutors added, {skipped} skipped')
            db.session.commit()
            flash(f'Uploaded: {added} tutors added, {skipped} skipped (already exist).', 'success')
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'danger')
        return redirect(url_for('admin.tutors'))

    return render_template('admin/upload_tutors.html')

@admin_bp.route('/upload-hods', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_hods():
    if request.method == 'POST':
        file = request.files.get('excel_file')
        if not file or not file.filename.endswith(('.xlsx', '.xls')):
            flash('Please upload a valid Excel file.', 'danger')
            return redirect(url_for('admin.upload_hods'))

        import pandas as pd
        try:
            df = pd.read_excel(file)
            required_cols = ['HOD Name', 'HOD Email', 'Department']
            if not all(col in df.columns for col in required_cols):
                flash(f'Excel must contain columns: {", ".join(required_cols)}', 'danger')
                return redirect(url_for('admin.upload_hods'))

            added, skipped = 0, 0
            default_password = bcrypt.hashpw('hod123'.encode(), bcrypt.gensalt()).decode()
            for _, row in df.iterrows():
                email = str(row['HOD Email']).strip().lower()
                if HOD.query.filter_by(email=email).first():
                    skipped += 1
                    continue
                hod = HOD(
                    hod_name=str(row['HOD Name']).strip(),
                    email=email,
                    department=str(row['Department']).strip(),
                    password=default_password,
                    must_change_password=True
                )
                db.session.add(hod)
                added += 1
            admin_log('HODs Uploaded', f'{added} HODs added, {skipped} skipped')
            db.session.commit()
            flash(f'Uploaded: {added} HODs added, {skipped} skipped.', 'success')
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'danger')
        return redirect(url_for('admin.hods'))

    return render_template('admin/upload_hods.html')

@admin_bp.route('/applications')
@login_required
@admin_required
def applications():
    apps = Application.query.order_by(Application.created_at.desc()).all()
    return render_template('admin/applications.html', apps=apps)

@admin_bp.route('/audit-log')
@login_required
@admin_required
def audit_log():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return render_template('admin/audit_log.html', logs=logs)

@admin_bp.route('/download-tutor-template')
@login_required
@admin_required
def download_tutor_template():
    import pandas as pd
    df = pd.DataFrame(columns=['Tutor Name', 'Tutor Email', 'Department', 'Year Handling', 'Section Handling'])
    df.loc[0] = ['Dr. Sample Tutor', 'tutor@ace.edu', 'Computer Science', 2, 'A']
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='tutor_upload_template.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@admin_bp.route('/download-hod-template')
@login_required
@admin_required
def download_hod_template():
    import pandas as pd
    df = pd.DataFrame(columns=['HOD Name', 'HOD Email', 'Department'])
    df.loc[0] = ['Dr. Sample HOD', 'hod@ace.edu', 'Computer Science']
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='hod_upload_template.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
