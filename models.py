from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid

db = SQLAlchemy()

class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    register_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=False)
    applications = db.relationship('Application', backref='student', lazy=True)

    def get_id(self):
        return f'student_{self.id}'

class Tutor(UserMixin, db.Model):
    __tablename__ = 'tutors'
    id = db.Column(db.Integer, primary_key=True)
    tutor_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year_handling = db.Column(db.Integer, nullable=False)
    section_handling = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    must_change_password = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('Application', backref='tutor', lazy=True, foreign_keys='Application.tutor_id')
    signature_path = db.Column(db.String(255), nullable=True)

    def get_id(self):
        return f'tutor_{self.id}'

class HOD(UserMixin, db.Model):
    __tablename__ = 'hods'
    id = db.Column(db.Integer, primary_key=True)
    hod_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    must_change_password = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('Application', backref='hod', lazy=True, foreign_keys='Application.hod_id')
    signature_path = db.Column(db.String(255), nullable=True)

    def get_id(self):
        return f'hod_{self.id}'

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return f'admin_{self.id}'

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(20), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.id'), nullable=True)
    tutor_name = db.Column(db.String(100), nullable=True)
    hod_id = db.Column(db.Integer, db.ForeignKey('hods.id'), nullable=True)
    event_name = db.Column(db.String(200), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    document_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='Pending Tutor Review')
    tutor_remark = db.Column(db.Text, nullable=True)
    hod_remark = db.Column(db.Text, nullable=True)
    tutor_reviewed_at = db.Column(db.DateTime, nullable=True)
    hod_reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_app_id():
        year = datetime.utcnow().strftime('%Y')
        count = Application.query.count() + 1
        return f'ACE-OD-{year}-{count:04d}'

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    performed_by = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
