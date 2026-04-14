from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import *
from extensions import db
from seed import CHATBOT_RESPONSES
from admin_routes import get_active_notifications

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'student':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@student_bp.route('/dashboard')
@student_required
def student_dashboard():
    student = Student.query.get(session['user_id'])
    notifications = get_active_notifications(student.branch)
    return render_template('student/dashboard.html', student=student, notifications=notifications)

@student_bp.route('/profile')
@student_required
def student_profile():
    student = Student.query.get(session['user_id'])
    return render_template('student/profile.html', student=student)

@student_bp.route('/results')
@student_required
def student_results():
    student = Student.query.get(session['user_id'])
    results = Result.query.filter_by(student_id=student.id).order_by(Result.semester).all()
    semesters = {}
    for r in results:
        semesters.setdefault(r.semester, []).append(r)
    return render_template('student/results.html', student=student, semesters=semesters)

@student_bp.route('/attendance')
@student_required
def student_attendance():
    student = Student.query.get(session['user_id'])
    attendance = Attendance.query.filter_by(student_id=student.id).all()
    return render_template('student/attendance.html', student=student, attendance=attendance)

@student_bp.route('/timetable')
@student_required
def student_timetable():
    student = Student.query.get(session['user_id'])
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    timetable = {}
    for day in days:
        slots = Timetable.query.filter_by(branch=student.branch, year=student.year, day=day)\
                               .order_by(Timetable.time_slot).all()
        timetable[day] = slots
    return render_template('student/timetable.html', student=student, timetable=timetable, days=days)

@student_bp.route('/fees')
@student_required
def student_fees():
    student = Student.query.get(session['user_id'])
    fees = Fee.query.filter_by(branch=student.branch, year=student.year).all()
    student_fees = StudentFee.query.filter_by(student_id=student.id).all()
    paid_ids = {sf.fee_id for sf in student_fees if sf.paid}
    return render_template('student/fees.html', student=student, fees=fees, paid_ids=paid_ids)

@student_bp.route('/placements')
@student_required
def student_placements():
    student = Student.query.get(session['user_id'])
    all_placements = Placement.query.order_by(Placement.posted_at.desc()).all()
    eligible = []
    not_eligible = []
    for p in all_placements:
        branches = [b.strip() for b in p.eligible_branches.split(',')]
        if student.branch in branches:
            eligible.append(p)
        else:
            not_eligible.append(p)
    return render_template('student/placements.html', student=student,
                           eligible=eligible, not_eligible=not_eligible)

@student_bp.route('/projects')
@student_required
def student_projects():
    student = Student.query.get(session['user_id'])
    projects = Project.query.filter_by(student_id=student.id).all()
    return render_template('student/projects.html', student=student, projects=projects)

@student_bp.route('/ranks')
@student_required
def student_ranks():
    student = Student.query.get(session['user_id'])
    ranks = Rank.query.filter_by(student_id=student.id).order_by(Rank.semester).all()
    return render_template('student/ranks.html', student=student, ranks=ranks)

@student_bp.route('/courses')
@student_required
def student_courses():
    student = Student.query.get(session['user_id'])
    courses = Course.query.filter_by(branch=student.branch, year=student.year).all()
    return render_template('student/courses.html', student=student, courses=courses)

@student_bp.route('/notifications')
@student_required
def student_notifications():
    student = Student.query.get(session['user_id'])
    notifications = get_active_notifications(student.branch)
    return render_template('student/notifications.html', student=student, notifications=notifications)

@student_bp.route('/associations')
@student_required
def student_associations():
    associations = Association.query.order_by(Association.event_date.desc()).all()
    student = Student.query.get(session['user_id'])
    return render_template('student/associations.html', student=student, associations=associations)

@student_bp.route('/chatbot', methods=['GET', 'POST'])
@student_required
def student_chatbot():
    reply = ""
    query = ""
    if request.method == 'POST':
        query = request.form.get('message', '')
        text = query.lower()
        reply = "Sorry, I didn't understand that. Try asking about admission, fees, courses, placements, or type 'help'."
        for key, response in CHATBOT_RESPONSES.items():
            if key in text:
                reply = response
                break
    return render_template('student/chatbot.html', query=query, reply=reply)
