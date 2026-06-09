from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import login_required, current_user
from models import db, Application, Student, Notification, AuditLog
from utils.pdf_generator import generate_od_pdf
from utils.excel_exporter import export_applications_excel
from utils.email_sender import send_email
from datetime import datetime

hod_bp = Blueprint('hod', __name__)

def hod_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'hod':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@hod_bp.route('/dashboard')
@login_required
@hod_required
def dashboard():
    apps = Application.query.filter_by(hod_id=current_user.id).order_by(Application.created_at.desc()).all()
    pending = [a for a in apps if a.status == 'Pending HOD Review']
    stats = {
        'total': len(apps),
        'pending': len(pending),
        'approved': len([a for a in apps if a.status == 'HOD Approved']),
        'rejected': len([a for a in apps if a.status == 'HOD Rejected']),
    }
    notifications = Notification.query.filter_by(
        user_id=str(current_user.id), user_type='hod', is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    return render_template('hod/dashboard.html', apps=apps, stats=stats, notifications=notifications, pending=pending)

@hod_bp.route('/applications')
@login_required
@hod_required
def applications():
    status_filter = request.args.get('status', '')
    query = Application.query.filter_by(hod_id=current_user.id)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    apps = query.order_by(Application.created_at.desc()).all()
    return render_template('hod/applications.html', apps=apps, status_filter=status_filter)

@hod_bp.route('/application/<int:app_id>', methods=['GET', 'POST'])
@login_required
@hod_required
def review_application(app_id):
    application = Application.query.filter_by(id=app_id, hod_id=current_user.id).first_or_404()

    if request.method == 'POST':
        action = request.form.get('action')
        remark = request.form.get('remark', '').strip()

        application.hod_remark = remark
        application.hod_reviewed_at = datetime.utcnow()
        student = db.session.get(Student, application.student_id)

        if action == 'approve':
            application.status = 'HOD Approved'
            log_action = 'HOD Approved'
            flash_msg = 'Application approved successfully.'
            email_msg = f'Congratulations! Your OD application {application.application_id} has been approved by HOD. You can now download your OD letter.'
        elif action == 'reject':
            application.status = 'HOD Rejected'
            log_action = 'HOD Rejected'
            flash_msg = 'Application rejected.'
            email_msg = f'Your OD application {application.application_id} has been rejected by HOD. Reason: {remark}'
        else:
            flash('Invalid action.', 'danger')
            return redirect(url_for('hod.review_application', app_id=app_id))

        log = AuditLog(application_id=application.application_id, action=log_action,
                       performed_by=current_user.hod_name, role='hod', remark=remark)
        db.session.add(log)

        notif = Notification(user_id=str(student.id), user_type='student',
                             message=f'Your application {application.application_id} has been {action}d by HOD.')
        db.session.add(notif)
        send_email(student.email, f'OD Application Final Decision - {application.application_id}', email_msg)

        db.session.commit()
        flash(flash_msg, 'success')
        return redirect(url_for('hod.applications'))

    logs = AuditLog.query.filter_by(application_id=application.application_id).all()
    return render_template('hod/review_application.html', application=application, logs=logs)

@hod_bp.route('/reports')
@login_required
@hod_required
def reports():
    from sqlalchemy import extract
    year_filter = request.args.get('year', '')
    month_filter = request.args.get('month', '')
    
    query = Application.query.filter_by(hod_id=current_user.id)
    if year_filter:
        query = query.filter(extract('year', Application.created_at) == int(year_filter))
    if month_filter:
        query = query.filter(extract('month', Application.created_at) == int(month_filter))
    
    apps = query.order_by(Application.created_at.desc()).all()
    return render_template('hod/reports.html', apps=apps, year_filter=year_filter, month_filter=month_filter)

@hod_bp.route('/export-excel')
@login_required
@hod_required
def export_excel():
    apps = Application.query.filter_by(hod_id=current_user.id).all()
    excel_path = export_applications_excel(apps, title=f'HOD_{current_user.hod_name}_Report')
    return send_file(excel_path, as_attachment=True, download_name='hod_report.xlsx')

@hod_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
@hod_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=str(current_user.id), user_type='hod').update({'is_read': True})
    db.session.commit()
    return redirect(url_for('hod.dashboard'))
