from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy import inspect, text
from config import Config
from models import db, Student, Tutor, HOD, Admin
from blueprints.auth import auth_bp
from blueprints.student import student_bp
from blueprints.tutor import tutor_bp
from blueprints.hod import hod_bp
from blueprints.admin import admin_bp
import os

mail = Mail()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(tutor_bp, url_prefix='/tutor')
    app.register_blueprint(hod_bp, url_prefix='/hod')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @login_manager.user_loader
    def load_user(user_id):
        user_type, uid = user_id.split('_', 1)
        if user_type == 'student':
            return db.session.get(Student, int(uid))
        elif user_type == 'tutor':
            return db.session.get(Tutor, int(uid))
        elif user_type == 'hod':
            return db.session.get(HOD, int(uid))
        elif user_type == 'admin':
            return db.session.get(Admin, int(uid))
        return None

    with app.app_context():
        db.create_all()
        ensure_schema_updates()
        create_default_admin(app)

    return app

def ensure_schema_updates():
    inspector = inspect(db.engine)
    if 'applications' not in inspector.get_table_names():
        return

    application_columns = {column['name'] for column in inspector.get_columns('applications')}
    if 'tutor_name' not in application_columns:
        with db.engine.begin() as connection:
            connection.execute(text('ALTER TABLE applications ADD COLUMN tutor_name VARCHAR(100)'))
    # add signature_path to tutors and hods if missing
    for tbl in ('tutors', 'hods'):
        if tbl in inspector.get_table_names():
            cols = {column['name'] for column in inspector.get_columns(tbl)}
            if 'signature_path' not in cols:
                try:
                    with db.engine.begin() as connection:
                        connection.execute(text(f'ALTER TABLE {tbl} ADD COLUMN signature_path VARCHAR(255)'))
                except Exception:
                    # ignore failures here; recommend running proper migrations in production
                    pass

def create_default_admin(app):
    from models import Admin
    import bcrypt
    if not Admin.query.first():
        hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
        admin = Admin(username='admin', email='admin@ace.edu', password=hashed)
        db.session.add(admin)
        db.session.commit()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
