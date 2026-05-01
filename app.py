from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, stream_with_context
from extensions import db
from werkzeug.security import check_password_hash, generate_password_hash
from models import Admin, Student
from seed import seed_data
from admin_routes import admin_bp
from student_routes import student_bp

app = Flask(__name__)
app.secret_key = 'gdc_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gdc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = True
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

db.init_app(app)

app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)

@app.route('/debug-db')
def debug_db():
    from models import Student, Admin

    students = Student.query.all()
    admins = Admin.query.all()

    student_data = [
        {
            "id": s.id,
            "name": s.name,
            "username": s.username,
            "branch": s.branch
        } for s in students
    ]

    admin_data = [
        {
            "id": a.id,
            "username": a.username
        } for a in admins
    ]

    return {
        "students": student_data,
        "admins": admin_data
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')

        if role == 'admin':
            admin = Admin.query.filter_by(username=username).first()
            if admin and check_password_hash(admin.password, password):
                session.permanent = True
                session['role'] = 'admin'
                session['user_id'] = admin.id
                session['name'] = admin.name or admin.username
                return redirect(url_for('admin.admin_dashboard'))
            return render_template('login.html', error="Invalid admin credentials")

        elif role in ('student', 'fresher'):
            student = Student.query.filter_by(username=username, account_created=True).first()
            if student and check_password_hash(student.password, password):
                session.permanent = True
                session['role'] = 'student'
                session['user_id'] = student.id
                session['name'] = student.name
                session['branch'] = student.branch
                return redirect(url_for('student.student_dashboard'))
            return render_template('login.html', error="Invalid credentials or account not activated")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        reg_number = request.form.get('reg_number').strip()
        username = request.form.get('username').strip()
        password = request.form.get('password')

        student = Student.query.filter_by(reg_number=reg_number).first()
        if not student:
            return render_template('register.html', error="Registration number not found. Contact admin.")
        if student.account_created:
            return render_template('register.html', error="Account already exists. Please login.")
        if Student.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already taken.")

        student.username = username
        student.password = generate_password_hash(password, method='pbkdf2:sha256')
        student.account_created = True
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/chatbot/api', methods=['POST'])
def public_chatbot_api():
    data = request.json if request.is_json else request.form
    query = data.get('message', '')
    history = data.get('history', [])
    from chatbot_engine import get_chatbot_response
    
    resp = Response(stream_with_context(get_chatbot_response(query, None, history)), mimetype='text/event-stream')
    resp.headers['X-Accel-Buffering'] = 'no'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=8000)
