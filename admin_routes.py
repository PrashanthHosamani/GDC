from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import *
from extensions import db
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_active_notifications(branch=None):
    now = datetime.utcnow()
    query = Notification.query.filter((Notification.expires_at == None) | (Notification.expires_at > now))
    if branch:
        query = query.filter((Notification.target_branch == 'all') | (Notification.target_branch == branch))
    return query.order_by(Notification.created_at.desc()).all()

# --- Admin: Students ---
@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_placements = Placement.query.count()
    active_notifications = len(get_active_notifications())
    branch_counts = {}
    for b in ['bca','bcom','bba','puc','mba']:
        branch_counts[b.upper()] = Student.query.filter_by(branch=b).count()
    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           total_placements=total_placements,
                           active_notifications=active_notifications,
                           branch_counts=branch_counts)

# --- Admin: Students ---
@admin_bp.route('/students', methods=['GET'])
@admin_required
def admin_students():
    branch = request.args.get('branch','')
    students = Student.query.filter_by(branch=branch).order_by(Student.name).all() if branch else Student.query.order_by(Student.name).all()
    return render_template('admin/students.html', students=students, selected_branch=branch)

@admin_bp.route('/students/add', methods=['GET','POST'])
@admin_required
def admin_add_student():
    if request.method == 'POST':
        reg = request.form.get('reg_number').strip()
        if Student.query.filter_by(reg_number=reg).first():
            flash('Registration number already exists.', 'error')
        else:
            db.session.add(Student(reg_number=reg, name=request.form.get('name'), branch=request.form.get('branch'), year=int(request.form.get('year', 1)), email=request.form.get('email'), phone=request.form.get('phone'), dob=request.form.get('dob'), address=request.form.get('address')))
            db.session.commit()
            flash('Student added successfully!', 'success')
        return redirect(url_for('admin.admin_students'))
    return render_template('admin/add_student.html')

@admin_bp.route('/students/bulk', methods=['GET','POST'])
@admin_required
def admin_bulk_students():
    if request.method == 'POST':
        lines, count, errors = request.form.get('data','').strip().split('\n'), 0, []
        for i, line in enumerate(lines, 1):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 4: errors.append(f"Row {i}: Need at least reg_number, name, branch, year"); continue
            if Student.query.filter_by(reg_number=parts[0]).first(): errors.append(f"Row {i}: {parts[0]} already exists"); continue
            db.session.add(Student(reg_number=parts[0], name=parts[1], branch=parts[2].lower(), year=int(parts[3]), email=parts[4] if len(parts)>4 else ''))
            count += 1
        db.session.commit()
        flash(f'{count} added. {len(errors)} errors.', 'warning' if errors else 'success')
        return render_template('admin/bulk_students.html', errors=errors)
    return render_template('admin/bulk_students.html', errors=[])

@admin_bp.route('/students/delete/<int:sid>', methods=['POST'])
@admin_required
def admin_delete_student(sid):
    db.session.delete(Student.query.get_or_404(sid)); db.session.commit()
    return redirect(url_for('admin.admin_students'))

@admin_bp.route('/notifications', methods=['GET', 'POST'])
@admin_required
def admin_notifications():
    if request.method == 'POST':
        h = request.form.get('hours', type=int)
        db.session.add(Notification(title=request.form.get('title'), message=request.form.get('message'), expires_at=datetime.utcnow()+timedelta(hours=h) if h else None, target_branch=request.form.get('branch', 'all')))
        db.session.commit()
        return redirect(url_for('admin.admin_notifications'))
    return render_template('admin/notifications.html', notifications=Notification.query.order_by(Notification.created_at.desc()).all(), now=datetime.utcnow())

@admin_bp.route('/notifications/delete/<int:nid>', methods=['POST'])
@admin_required
def admin_delete_notification(nid):
    db.session.delete(Notification.query.get_or_404(nid)); db.session.commit()
    return redirect(url_for('admin.admin_notifications'))

@admin_bp.route('/fees', methods=['GET', 'POST'])
@admin_required
def admin_fees():
    if request.method == 'POST':
        db.session.add(Fee(branch=request.form.get('branch'), year=int(request.form.get('year')), amount=float(request.form.get('amount')), description=request.form.get('description'), due_date=request.form.get('due_date')))
        db.session.commit()
        return redirect(url_for('admin.admin_fees'))
    return render_template('admin/fees.html', fees=Fee.query.order_by(Fee.branch, Fee.year).all())

@admin_bp.route('/fees/delete/<int:fid>', methods=['POST'])
@admin_required
def admin_delete_fee(fid):
    db.session.delete(Fee.query.get_or_404(fid)); db.session.commit()
    return redirect(url_for('admin.admin_fees'))

@admin_bp.route('/courses', methods=['GET', 'POST'])
@admin_required
def admin_courses():
    if request.method == 'POST':
        db.session.add(Course(branch=request.form.get('branch'), year=int(request.form.get('year')), name=request.form.get('name'), code=request.form.get('code'), credits=int(request.form.get('credits', 0)), description=request.form.get('description')))
        db.session.commit()
        return redirect(url_for('admin.admin_courses'))
    return render_template('admin/courses.html', courses=Course.query.order_by(Course.branch, Course.year).all())

@admin_bp.route('/courses/delete/<int:cid>', methods=['POST'])
@admin_required
def admin_delete_course(cid):
    db.session.delete(Course.query.get_or_404(cid)); db.session.commit()
    return redirect(url_for('admin.admin_courses'))

@admin_bp.route('/placements', methods=['GET', 'POST'])
@admin_required
def admin_placements():
    if request.method == 'POST':
        db.session.add(Placement(company_name=request.form.get('company_name'), job_role=request.form.get('job_role'), description=request.form.get('description'), salary_min=float(request.form.get('salary_min') or 0), salary_max=float(request.form.get('salary_max') or 0), drive_date=request.form.get('drive_date'), eligible_branches=','.join(request.form.getlist('branches')), min_percentage=float(request.form.get('min_percentage') or 60), status=request.form.get('status','upcoming')))
        db.session.commit()
        return redirect(url_for('admin.admin_placements'))
    return render_template('admin/placements.html', placements=Placement.query.order_by(Placement.posted_at.desc()).all())

@admin_bp.route('/placements/delete/<int:pid>', methods=['POST'])
@admin_required
def admin_delete_placement(pid):
    db.session.delete(Placement.query.get_or_404(pid)); db.session.commit()
    return redirect(url_for('admin.admin_placements'))

@admin_bp.route('/ranks', methods=['GET', 'POST'])
@admin_required
def admin_ranks():
    if request.method == 'POST':
        db.session.add(Rank(student_id=int(request.form.get('student_id')), semester=int(request.form.get('semester')), rank=int(request.form.get('rank')), sgpa=float(request.form.get('sgpa')), year=int(request.form.get('year'))))
        db.session.commit()
        return redirect(url_for('admin.admin_ranks'))
    return render_template('admin/ranks.html', ranks=db.session.query(Rank, Student).join(Student).order_by(Rank.semester, Rank.rank).all(), students=Student.query.order_by(Student.name).all())

@admin_bp.route('/associations', methods=['GET', 'POST'])
@admin_required
def admin_associations():
    if request.method == 'POST':
        db.session.add(Association(name=request.form.get('name'), description=request.form.get('description'), event_date=request.form.get('event_date'), category=request.form.get('category'), contact=request.form.get('contact')))
        db.session.commit()
        return redirect(url_for('admin.admin_associations'))
    return render_template('admin/associations.html', associations=Association.query.order_by(Association.event_date.desc()).all())

@admin_bp.route('/associations/delete/<int:aid>', methods=['POST'])
@admin_required
def admin_delete_association(aid):
    db.session.delete(Association.query.get_or_404(aid)); db.session.commit()
    return redirect(url_for('admin.admin_associations'))

@admin_bp.route('/results', methods=['GET', 'POST'])
@admin_required
def admin_results():
    if request.method == 'POST':
        db.session.add(Result(student_id=int(request.form.get('student_id')), semester=int(request.form.get('semester')), subject=request.form.get('subject'), marks=float(request.form.get('marks')), max_marks=float(request.form.get('max_marks', 100)), grade=request.form.get('grade'), year=int(request.form.get('year'))))
        db.session.commit()
        return redirect(url_for('admin.admin_results'))
    return render_template('admin/results.html', students=Student.query.order_by(Student.name).all())

@admin_bp.route('/attendance', methods=['GET', 'POST'])
@admin_required
def admin_attendance():
    if request.method == 'POST':
        db.session.add(Attendance(student_id=int(request.form.get('student_id')), subject=request.form.get('subject'), total_classes=int(request.form.get('total_classes')), attended=int(request.form.get('attended')), semester=int(request.form.get('semester'))))
        db.session.commit()
        return redirect(url_for('admin.admin_attendance'))
    return render_template('admin/attendance.html', students=Student.query.order_by(Student.name).all())

@admin_bp.route('/timetable', methods=['GET', 'POST'])
@admin_required
def admin_timetable():
    if request.method == 'POST':
        db.session.add(Timetable(branch=request.form.get('branch'), year=int(request.form.get('year')), day=request.form.get('day'), time_slot=request.form.get('time_slot'), subject=request.form.get('subject'), teacher=request.form.get('teacher'), room=request.form.get('room')))
        db.session.commit()
        return redirect(url_for('admin.admin_timetable'))
    return render_template('admin/timetable.html', timetables=Timetable.query.order_by(Timetable.branch, Timetable.day).all())

@admin_bp.route('/timetable/delete/<int:tid>', methods=['POST'])
@admin_required
def admin_delete_timetable(tid):
    db.session.delete(Timetable.query.get_or_404(tid)); db.session.commit()
    return redirect(url_for('admin.admin_timetable'))

@admin_bp.route('/timetable/edit/<int:tid>', methods=['GET', 'POST'])
@admin_required
def admin_edit_timetable(tid):
    t = Timetable.query.get_or_404(tid)
    if request.method == 'POST':
        t.branch = request.form.get('branch')
        t.year = int(request.form.get('year'))
        t.day = request.form.get('day')
        t.time_slot = request.form.get('time_slot')
        t.subject = request.form.get('subject')
        t.teacher = request.form.get('teacher')
        t.room = request.form.get('room')
        db.session.commit()
        flash('Timetable updated!', 'success')
        return redirect(url_for('admin.admin_timetable'))
    return render_template('admin/edit_timetable.html', t=t)


@admin_bp.route('/projects', methods=['GET', 'POST'])
@admin_required
def admin_projects():
    if request.method == 'POST':
        db.session.add(Project(student_id=int(request.form.get('student_id')), title=request.form.get('title'), description=request.form.get('description'), subject=request.form.get('subject'), guide=request.form.get('guide'), status=request.form.get('status','ongoing'), semester=int(request.form.get('semester'))))
        db.session.commit()
        return redirect(url_for('admin.admin_projects'))
    return render_template('admin/projects.html', projects=db.session.query(Project, Student).join(Student).order_by(Project.semester).all(), students=Student.query.order_by(Student.name).all())
