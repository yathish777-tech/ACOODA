from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Student, Tutor, HOD, Admin
import bcrypt
import re

auth_bp = Blueprint('auth', __name__)

ROLE_MODELS = (
    ('admin', Admin),
    ('student', Student),
    ('tutor', Tutor),
    ('hod', HOD),
)

ROLE_DASHBOARDS = {
    'student': 'student.dashboard',
    'tutor': 'tutor.dashboard',
    'hod': 'hod.dashboard',
    'admin': 'admin.dashboard',
}

def resolve_login_user(email, password):
    email = (email or '').strip().lower()
    password_bytes = (password or '').encode()

    for role, model in ROLE_MODELS:
        user = model.query.filter(db.func.lower(model.email) == email).first()
        if user and bcrypt.checkpw(password_bytes, user.password.encode()):
            return role, user
    return None, None

def find_user_by_email(email):
    email = (email or '').strip().lower()
    for role, model in ROLE_MODELS:
        user = model.query.filter(db.func.lower(model.email) == email).first()
        if user:
            return role, user
    return None, None

def password_errors(password):
    checks = [
        (len(password) >= 8, 'Minimum 8 characters'),
        (re.search(r'[A-Z]', password), 'One uppercase letter'),
        (re.search(r'[a-z]', password), 'One lowercase letter'),
        (re.search(r'\d', password), 'One number'),
        (re.search(r'[^A-Za-z0-9]', password), 'One special character'),
    ]
    return [message for passed, message in checks if not passed]

def redirect_for_role(role):
    return redirect(url_for(ROLE_DASHBOARDS.get(role, 'auth.login')))

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == 'on'
        role, user = resolve_login_user(email, password)

        if user:
            if hasattr(user, 'is_active') and not user.is_active:
                flash('Your account has been deactivated. Contact admin.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            session['role'] = role

            if hasattr(user, 'must_change_password') and user.must_change_password:
                flash('Please change your default password before continuing.', 'warning')
                return redirect(url_for('auth.change_password'))

            return redirect_for_role(role)
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        register_no = request.form.get('register_no', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', '').strip()
        section = request.form.get('section', '').strip()
        year = int(request.form.get('year', 1))
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        if Student.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        if Student.query.filter_by(register_no=register_no).first():
            flash('Register number already exists.', 'danger')
            return redirect(url_for('auth.register'))

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        student = Student(
            register_no=register_no, name=name, email=email,
            department=department, section=section, year=year, password=hashed
        )
        db.session.add(student)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.index'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not bcrypt.checkpw(current_password.encode(), current_user.password.encode()):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('auth.change_password'))

        errors = password_errors(new_password)
        if errors:
            flash('Password must include: ' + ', '.join(errors) + '.', 'danger')
            return redirect(url_for('auth.change_password'))

        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        current_user.password = hashed
        if hasattr(current_user, 'must_change_password'):
            current_user.must_change_password = False
        db.session.commit()
        flash('Password changed successfully!', 'success')
        
        role = session.get('role')
        if role in ROLE_DASHBOARDS:
            return redirect_for_role(role)
        return redirect(url_for('auth.login'))

    return render_template('auth/change_password.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        role, user = find_user_by_email(email)
        
        if user:
            flash('If this email exists, a reset link has been sent. (Email service required)', 'info')
        else:
            flash('If this email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')
