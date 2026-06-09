from flask import current_app
import logging

def send_email(to_email, subject, body):
    """Send email notification. Gracefully handles missing mail config."""
    try:
        from flask_mail import Message
        from app import mail
        msg = Message(subject=subject, recipients=[to_email], body=body)
        mail.send(msg)
        logging.info(f'Email sent to {to_email}: {subject}')
    except Exception as e:
        logging.warning(f'Email not sent to {to_email}: {str(e)}')

def send_html_email(to_email, subject, html_body):
    """Send HTML email notification."""
    try:
        from flask_mail import Message
        from app import mail
        msg = Message(subject=subject, recipients=[to_email], html=html_body)
        mail.send(msg)
    except Exception as e:
        logging.warning(f'HTML Email not sent to {to_email}: {str(e)}')
