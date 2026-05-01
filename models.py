from extensions import db
from datetime import datetime

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_number = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(20))   # bca, bcom, bba, puc, mba, bca(m), bcom(m), bba(m), mba(m)
    year = db.Column(db.Integer)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    account_created = db.Column(db.Boolean, default=False)
    dob = db.Column(db.String(20))
    address = db.Column(db.String(200))
    photo = db.Column(db.String(200), default='default.png')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    target_branch = db.Column(db.String(20), default='all')  # all / bca / bcom / bca(m) / bcom(m) etc

class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(20), nullable=False)  # Supports: bca, bcom, bba, puc, mba, bca(m), bcom(m), bba(m), mba(m)
    year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    due_date = db.Column(db.String(30))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudentFee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    fee_id = db.Column(db.Integer, db.ForeignKey('fee.id'))
    paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.String(30))
    receipt_no = db.Column(db.String(50))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    credits = db.Column(db.Integer)
    description = db.Column(db.Text)

class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    job_role = db.Column(db.String(100))
    description = db.Column(db.Text)
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    drive_date = db.Column(db.String(30))
    eligible_branches = db.Column(db.String(200))  # comma-separated
    min_percentage = db.Column(db.Float, default=60.0)
    status = db.Column(db.String(20), default='upcoming')  # upcoming / completed
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    semester = db.Column(db.Integer)
    subject = db.Column(db.String(100))
    marks = db.Column(db.Float)
    max_marks = db.Column(db.Float, default=100)
    grade = db.Column(db.String(5))
    year = db.Column(db.Integer)

class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer)
    day = db.Column(db.String(15))
    time_slot = db.Column(db.String(30))
    subject = db.Column(db.String(100))
    teacher = db.Column(db.String(100))
    room = db.Column(db.String(20))

class Association(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.String(30))
    category = db.Column(db.String(50))  # NSS, NCC, Club, Sports
    contact = db.Column(db.String(100))
