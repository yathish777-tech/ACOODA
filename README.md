<<<<<<< HEAD
# ACOODA — Adhiyamaan College Online On-Duty Application System

> Digital OD Approval System for Adhiyamaan College of Engineering, Hosur

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

**Option A — SQLite (Recommended for development):**
Edit `config.py` line 8:
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///acooda.db'
```

**Option B — MySQL (Production):**
```sql
CREATE DATABASE acooda_db CHARACTER SET utf8mb4;
CREATE USER 'acooda'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON acooda_db.* TO 'acooda'@'localhost';
```
Then update `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://acooda:yourpassword@localhost/acooda_db'
```

### 3. Configure Email (Optional)
Edit `config.py`:
```python
MAIL_USERNAME = 'your@gmail.com'
MAIL_PASSWORD = 'your-app-password'
```
> Enable "App Passwords" in your Google account for Gmail.

### 4. Run the App

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## 🔐 Default Credentials

| Role    | Email               | Password  | Notes                        |
|---------|---------------------|-----------|------------------------------|
| Admin   | admin@ace.edu       | admin123  | Created automatically        |
| Tutor   | (from Excel upload) | staff123  | Must change on first login   |
| HOD     | (from Excel upload) | hod123    | Must change on first login   |
| Student | Self-registered     | (chosen)  | Register at /register        |

---

## 📁 Project Structure

```
acooda/
├── app.py                  # Application factory & entry point
├── config.py               # Configuration (DB, Mail, etc.)
├── models.py               # SQLAlchemy database models
├── requirements.txt        # Python dependencies
├── run.sh                  # Quick-start shell script
│
├── blueprints/
│   ├── auth.py             # Login, Register, Forgot Password
│   ├── student.py          # Student dashboard & OD application
│   ├── tutor.py            # Tutor review dashboard
│   ├── hod.py              # HOD approval dashboard & reports
│   └── admin.py            # Admin panel, Excel uploads
│
├── utils/
│   ├── pdf_generator.py    # ReportLab OD letter PDF generator
│   ├── excel_exporter.py   # OpenPyXL Excel export
│   └── email_sender.py     # Flask-Mail email notifications
│
├── templates/
│   ├── base.html           # Shared dashboard layout
│   ├── index.html          # Landing page
│   ├── auth/               # Login, Register, Change Password
│   ├── student/            # Student dashboard, apply, view
│   ├── tutor/              # Tutor dashboard & review
│   ├── hod/                # HOD dashboard, review, reports
│   └── admin/              # Admin dashboard, uploads, users
│
└── static/
    ├── css/style.css       # Complete responsive stylesheet
    ├── js/main.js          # Frontend JS (sidebar, drag-drop...)
    ├── images/             # College logo & campus background
    └── uploads/            # Student uploaded documents
```

---

## 👥 User Roles & Workflow

```
Student registers → Applies for OD
       ↓
Tutor receives email notification
       ↓
Tutor reviews → Approves & forwards to HOD
       ↓
HOD receives email notification
       ↓
HOD gives final approval/rejection
       ↓
Student receives email → Downloads OD PDF
```

### Role Features

| Feature                     | Student | Tutor | HOD | Admin |
|-----------------------------|:-------:|:-----:|:---:|:-----:|
| Self Registration           | ✅      |       |     |       |
| Apply for OD                | ✅      |       |     |       |
| View own applications       | ✅      |       |     |       |
| Download OD PDF             | ✅      |       |     | ✅    |
| View assigned class apps    |         | ✅    |     |       |
| Approve / Reject            |         | ✅    | ✅  |       |
| Export to Excel             |         | ✅    | ✅  | ✅    |
| Department reports          |         |       | ✅  |       |
| Upload tutors via Excel     |         |       |     | ✅    |
| Upload HODs via Excel       |         |       |     | ✅    |
| Activate/Deactivate users   |         |       |     | ✅    |
| System Audit Log            |         |       |     | ✅    |
| Email notifications         | ✅      | ✅    | ✅  |       |

---

## 📊 OD Application Status Flow

```
Pending Tutor Review → Tutor Approved → Pending HOD Review → HOD Approved ✅
                    ↘ Tutor Rejected ❌
                                      ↘ HOD Rejected ❌
```

---

## 📋 Excel Upload Formats

### Tutor Upload (`admin → Upload Tutors`)

| Tutor Name   | Tutor Email       | Department              | Year Handling | Section Handling |
|--------------|-------------------|-------------------------|:-------------:|:----------------:|
| Dr. A. Kumar | tutor@ace.edu     | Computer Science...     | 2             | A                |

Download template from Admin → Upload Tutors → **Download Template**

### HOD Upload (`admin → Upload HODs`)

| HOD Name    | HOD Email     | Department              |
|-------------|---------------|-------------------------|
| Dr. B. Raj  | hod@ace.edu   | Computer Science...     |

---

## 🔧 Tech Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Backend  | Python Flask + Blueprints               |
| Database | MySQL (prod) / SQLite (dev)             |
| ORM      | Flask-SQLAlchemy                        |
| Auth     | Flask-Login + bcrypt                    |
| PDF      | ReportLab                               |
| Excel    | OpenPyXL + Pandas                       |
| Email    | Flask-Mail                              |
| Frontend | HTML5 + CSS3 (custom) + Vanilla JS      |
| Icons    | Font Awesome 6                          |
| Fonts    | Google Fonts (Inter + Playfair Display) |

---

## 🛡️ Security Features

- bcrypt password hashing
- Flask-Login session management
- Role-based access control (student/tutor/hod/admin)
- Mandatory first-login password change for staff
- Input validation on all forms
- Secure file upload with extension validation
- SQL Injection protection via SQLAlchemy ORM
- Audit log for all approval actions

---

## 🎨 UI Highlights

- College branding (logo, campus background)
- Responsive sidebar layout (mobile-friendly)
- Color-coded status badges
- Approval timeline visualization
- Drag & drop file upload
- Auto-dismissing flash messages
- Professional OD letter PDF with college header, signatures area

---

## 📝 OD Reason Categories

Symposium, Workshop, Internship, Placement Training, Hackathon,
Project Presentation, Technical Event, Sports Event, NSS/NCC Activity,
Industrial Visit, Other

---

## 🗄️ Database Tables

- `students` — Registered students
- `tutors` — Uploaded by admin via Excel
- `hods` — Uploaded by admin via Excel
- `admins` — System administrators
- `applications` — OD application records
- `notifications` — In-app notifications
- `audit_logs` — Complete action audit trail

---

*Built for Adhiyamaan College of Engineering, Hosur — Achieve Create Excel*
=======
# ACOODA
Adhiyamaan College Online On Duty Application
>>>>>>> 021276653ab42a20c1f4278a5181ce165cabd44a
