from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import login_required, current_user
from models import db, Application, Student, Notification, AuditLog, HOD
from utils.assignments import backfill_unassigned_applications_for_tutor
from utils.pdf_generator import generate_od_pdf
from utils.excel_exporter import export_applications_excel
from utils.email_sender import send_email
from datetime import datetime

tutor_bp = Blueprint('tutor', __name__)

def tutor_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'tutor':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def sync_tutor_assignments():
    updated = backfill_unassigned_applications_for_tutor(current_user)
    if updated:
        db.session.commit()

@tutor_bp.route('/dashboard')
@login_required
@tutor_required
def dashboard():
    sync_tutor_assignments()
    apps = Application.query.filter_by(tutor_id=current_user.id).order_by(Application.created_at.desc()).all()
    pending_apps = [a for a in apps if a.status == 'Pending Tutor Review']
    approved_apps = [a for a in apps if a.status in ['Tutor Approved', 'Pending HOD Review', 'HOD Approved', 'HOD Rejected']]
    rejected_apps = [a for a in apps if 'Rejected' in a.status]
    stats = {
        'total': len(apps),
        'pending': len(pending_apps),
        'approved': len(approved_apps),
        'rejected': len(rejected_apps),
    }
    notifications = Notification.query.filter_by(
        user_id=str(current_user.id), user_type='tutor', is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    return render_template(
        'tutor/dashboard.html',
        apps=apps,
        stats=stats,
        notifications=notifications,
        pending_apps=pending_apps,
        approved_apps=approved_apps,
        rejected_apps=rejected_apps
    )

@tutor_bp.route('/applications')
@login_required
@tutor_required
def applications():
    sync_tutor_assignments()
    status_filter = request.args.get('status', '')
    query = Application.query.filter_by(tutor_id=current_user.id)
    if status_filter:
        if status_filter == 'Approved':
            query = query.filter(Application.status.in_(['Tutor Approved', 'Pending HOD Review', 'HOD Approved', 'HOD Rejected']))
        elif status_filter == 'Rejected':
            query = query.filter(Application.status.like('%Rejected%'))
        elif status_filter == 'Pending':
            query = query.filter(Application.status == 'Pending Tutor Review')
        else:
            query = query.filter(Application.status == status_filter)
    apps = query.order_by(Application.created_at.desc()).all()
    return render_template('tutor/applications.html', apps=apps, status_filter=status_filter)

@tutor_bp.route('/application/<int:app_id>', methods=['GET', 'POST'])
@login_required
@tutor_required
def review_application(app_id):
    application = Application.query.filter_by(id=app_id, tutor_id=current_user.id).first_or_404()

    if request.method == 'POST':
        action = request.form.get('action')
        remark = request.form.get('remark', '').strip()

        application.tutor_remark = remark
        application.tutor_reviewed_at = datetime.utcnow()
        student = db.session.get(Student, application.student_id)

        if action == 'approve':
            application.status = 'Pending HOD Review'
            # Notify HOD
            hod = db.session.get(HOD, application.hod_id)
            if hod:
                notif = Notification(user_id=str(hod.id), user_type='hod',
                                     message=f'Application {application.application_id} forwarded for HOD review')
                db.session.add(notif)
                send_email(hod.email, f'OD Application for Review - {application.application_id}',
                           f'Tutor {current_user.tutor_name} has approved and forwarded OD application {application.application_id} from {student.name} for your review.')
            log_action = 'Tutor Approved & Forwarded to HOD'
            flash_msg = 'Application approved and forwarded to HOD.'
        elif action == 'reject':
            application.status = 'Tutor Rejected'
            log_action = 'Tutor Rejected'
            flash_msg = 'Application rejected.'
        else:
            flash('Invalid action.', 'danger')
            return redirect(url_for('tutor.review_application', app_id=app_id))

        log = AuditLog(application_id=application.application_id, action=log_action,
                       performed_by=current_user.tutor_name, role='tutor', remark=remark)
        db.session.add(log)

        # Notify student
        notif = Notification(user_id=str(student.id), user_type='student',
                             message=f'Your application {application.application_id} has been {action}d by Tutor.')
        db.session.add(notif)
        send_email(student.email, f'OD Application Update - {application.application_id}',
                   f'Your OD application {application.application_id} status: {application.status}. Remark: {remark}')

        db.session.commit()
        flash(flash_msg, 'success')
        return redirect(url_for('tutor.applications'))

    logs = AuditLog.query.filter_by(application_id=application.application_id).all()
    return render_template('tutor/review_application.html', application=application, logs=logs)

@tutor_bp.route('/application/<int:app_id>/pdf')
@login_required
@tutor_required
def download_pdf(app_id):
    application = Application.query.filter_by(id=app_id, tutor_id=current_user.id).first_or_404()
    student = db.session.get(Student, application.student_id)
    pdf_path = generate_od_pdf(application, student)
    return send_file(pdf_path, as_attachment=True, download_name=f'OD_{application.application_id}.pdf')

@tutor_bp.route('/export-excel')
@login_required
@tutor_required
def export_excel():
    apps = Application.query.filter_by(tutor_id=current_user.id).all()
    excel_path = export_applications_excel(apps, title=f'Tutor_{current_user.tutor_name}_Applications')
    return send_file(excel_path, as_attachment=True, download_name='tutor_applications.xlsx')

@tutor_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
@tutor_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=str(current_user.id), user_type='tutor').update({'is_read': True})
    db.session.commit()
    return redirect(url_for('tutor.dashboard'))
