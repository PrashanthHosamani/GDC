from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response, stream_with_context
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

@student_bp.route('/timetable')
@student_required
def student_timetable():
    student = Student.query.get(session['user_id'])
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    timetable = {}
    for day in days:
        # Try to get timetable for exact branch (merit-based)
        slots = Timetable.query.filter_by(branch=student.branch, year=student.year, day=day)\
                               .order_by(Timetable.time_slot).all()
        # If not found and merit-based, try base branch
        if not slots and '(m)' in student.branch:
            base_branch = student.branch.replace('(m)', '')
            slots = Timetable.query.filter_by(branch=base_branch, year=student.year, day=day)\
                                   .order_by(Timetable.time_slot).all()
        timetable[day] = slots
    return render_template('student/timetable.html', student=student, timetable=timetable, days=days)

@student_bp.route('/fees')
@student_required
def student_fees():
    student = Student.query.get(session['user_id'])
    # Get fees for the exact branch only
    fees = Fee.query.filter_by(branch=student.branch, year=student.year).all()
    
    student_fees = StudentFee.query.filter_by(student_id=student.id).all()
    paid_ids = {sf.fee_id for sf in student_fees if sf.paid}
    return render_template('student/fees.html', student=student, fees=fees, paid_ids=paid_ids)

@student_bp.route('/fees/mark-paid/<int:fee_id>', methods=['POST'])
@student_required
def mark_fee_paid(fee_id):
    student = Student.query.get(session['user_id'])
    fee = Fee.query.get_or_404(fee_id)
    
    # Check if student fee record exists
    student_fee = StudentFee.query.filter_by(student_id=student.id, fee_id=fee_id).first()
    
    if not student_fee:
        student_fee = StudentFee(student_id=student.id, fee_id=fee_id)
        db.session.add(student_fee)
    
    student_fee.paid = True
    student_fee.paid_date = datetime.now().strftime('%Y-%m-%d')
    db.session.commit()
    flash('Fee marked as paid via office. Please verify with admin if needed.', 'success')
    return redirect(url_for('student.student_fees'))

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


@student_bp.route('/chatbot/api', methods=['POST'])
@student_required
def student_chatbot_api():
    data = request.json if request.is_json else request.form
    query = data.get('message', '')
    history = data.get('history', [])
    student = Student.query.get(session['user_id'])
    from chatbot_engine import get_chatbot_response
    
    resp = Response(stream_with_context(get_chatbot_response(query, student, history)), mimetype='text/event-stream')
    resp.headers['X-Accel-Buffering'] = 'no'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp
