from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import login_required, current_user
from models import db, Application, Notification, AuditLog
from utils.assignments import find_hod_for_student, find_tutor_for_student
from utils.pdf_generator import generate_od_pdf
from utils.email_sender import send_email
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from config import Config

student_bp = Blueprint('student', __name__)

def student_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'student':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    apps = Application.query.filter_by(student_id=current_user.id).order_by(Application.created_at.desc()).all()
    stats = {
        'total': len(apps),
        'pending': len([a for a in apps if 'Pending' in a.status]),
        'approved': len([a for a in apps if a.status == 'HOD Approved']),
        'rejected': len([a for a in apps if 'Rejected' in a.status]),
    }
    notifications = Notification.query.filter_by(
        user_id=str(current_user.id), user_type='student', is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    return render_template('student/dashboard.html', apps=apps, stats=stats, notifications=notifications)

@student_bp.route('/apply', methods=['GET', 'POST'])
@login_required
@student_required
def apply():
    tutor = find_tutor_for_student(current_user)

    if request.method == 'POST':
        event_name = request.form.get('event_name', '').strip()
        event_date = request.form.get('event_date')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        reason = request.form.get('reason', '').strip()
        description = request.form.get('description', '').strip()

        if not all([event_name, event_date, from_date, to_date, reason, description]):
            flash('Please fill all required fields.', 'danger')
            return redirect(url_for('student.apply'))

        tutor = find_tutor_for_student(current_user)
        if not tutor:
            flash('No tutor is mapped for your year and section yet. Please contact the admin office.', 'danger')
            return redirect(url_for('student.apply'))

        doc_path = None
        if 'document' in request.files:
            file = request.files['document']
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[-1].lower()
                if ext in Config.ALLOWED_EXTENSIONS:
                    fname = secure_filename(f"{current_user.register_no}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}")
                    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                    file.save(os.path.join(Config.UPLOAD_FOLDER, fname))
                    doc_path = fname

        app_id = Application.generate_app_id()
        hod = find_hod_for_student(current_user)

        application = Application(
            application_id=app_id,
            student_id=current_user.id,
            tutor_id=tutor.id,
            tutor_name=tutor.tutor_name,
            hod_id=hod.id if hod else None,
            event_name=event_name,
            event_date=datetime.strptime(event_date, '%Y-%m-%d').date(),
            from_date=datetime.strptime(from_date, '%Y-%m-%d').date(),
            to_date=datetime.strptime(to_date, '%Y-%m-%d').date(),
            reason=reason,
            description=description,
            document_path=doc_path,
            status='Pending Tutor Review'
        )
        db.session.add(application)

        # Audit log
        log = AuditLog(application_id=app_id, action='Application Submitted',
                       performed_by=current_user.name, role='student')
        db.session.add(log)

        # Notify tutor
        notif = Notification(user_id=str(tutor.id), user_type='tutor',
                             message=f'New OD application {app_id} from {current_user.name}')
        db.session.add(notif)
        send_email(tutor.email, f'New OD Application - {app_id}',
                   f'Student {current_user.name} has submitted OD application {app_id} for {event_name}.')

        db.session.commit()

        # Notify student
        student_notif = Notification(user_id=str(current_user.id), user_type='student',
                                     message=f'Your application {app_id} has been assigned to {tutor.tutor_name}.')
        db.session.add(student_notif)
        db.session.commit()

        flash(f'Application {app_id} submitted successfully and assigned to {tutor.tutor_name}.', 'success')
        return redirect(url_for('student.my_applications'))

    return render_template('student/apply.html', tutor=tutor)

@student_bp.route('/applications')
@login_required
@student_required
def my_applications():
    status_filter = request.args.get('status', '')
    query = Application.query.filter_by(student_id=current_user.id)
    if status_filter:
        query = query.filter(Application.status.like(f'%{status_filter}%'))
    apps = query.order_by(Application.created_at.desc()).all()
    return render_template('student/applications.html', apps=apps, status_filter=status_filter)

@student_bp.route('/application/<int:app_id>')
@login_required
@student_required
def view_application(app_id):
    application = Application.query.filter_by(id=app_id, student_id=current_user.id).first_or_404()
    logs = AuditLog.query.filter_by(application_id=application.application_id).order_by(AuditLog.created_at).all()
    return render_template('student/view_application.html', application=application, logs=logs)

@student_bp.route('/application/<int:app_id>/download-pdf')
@login_required
@student_required
def download_pdf(app_id):
    application = Application.query.filter_by(id=app_id, student_id=current_user.id).first_or_404()
    pdf_path = generate_od_pdf(application, current_user)
    return send_file(pdf_path, as_attachment=True, download_name=f'OD_{application.application_id}.pdf')

@student_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
@student_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=str(current_user.id), user_type='student').update({'is_read': True})
    db.session.commit()
    return redirect(url_for('student.dashboard'))
