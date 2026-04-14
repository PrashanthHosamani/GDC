from models import *
from extensions import db
from werkzeug.security import generate_password_hash

CHATBOT_RESPONSES = {
    "admission": "Admissions at GDC open in May. Courses offered: BCA, BBA, BCom, PUC, MBA. Visit the college office or call for details.",
    "fees": "Fees vary by course: BCA ~₹45,000/yr, BBA ~₹40,000/yr, BCom ~₹35,000/yr, MBA ~₹80,000/yr. Check the Fees section for exact details.",
    "placement": "GDC has excellent placement support. Top IT and management companies visit campus. Average package is ₹3-5 LPA.",
    "exam": "Exam timetables are posted on the notice board and the portal. Check the Notifications section for updates.",
    "sports": "Sports Day is conducted every January. GDC participates in university-level tournaments as well.",
    "calendar": "Holidays include Dasara, Christmas, Eid, and a 2-month Summer vacation. Check the college website for the full academic calendar.",
    "nss": "NSS (National Service Scheme) is active at GDC. Students can enroll at the beginning of the academic year.",
    "ncc": "NCC (National Cadet Corps) is available for interested students. Contact the NCC officer for enrollment.",
    "bca": "BCA (Bachelor of Computer Applications) is a 3-year program focused on software, programming, and IT skills.",
    "bcom": "BCom (Bachelor of Commerce) covers accounting, finance, and business administration over 3 years.",
    "bba": "BBA (Bachelor of Business Administration) is a management-focused 3-year undergraduate program.",
    "mba": "MBA (Master of Business Administration) is a 2-year postgraduate program in management.",
    "puc": "PUC (Pre-University Course) is a 2-year program. GDC offers Science and Commerce streams.",
    "library": "The GDC library is open from 9 AM to 5 PM on weekdays. It has a large collection of books and digital resources.",
    "hostel": "Hostel facilities are available for outstation students. Contact the admin office for room availability.",
    "scholarship": "Various scholarships are available for merit and SC/ST/OBC students. Check with the admin office for eligibility.",
    "contact": "GDC Contact: Surathkal-575014, D.K. Phone: 0824-XXXXXXX. Email: info@gdc.edu.in",
    "result": "Results are published on the Mangalore University website and also on the student portal here.",
    "attendance": "Minimum 75% attendance is required to appear for exams. Check your attendance in the student portal.",
    "hello": "Hello! 👋 I'm GDC Buddy. Ask me about admissions, fees, courses, placements, or anything about college!",
    "hi": "Hi there! 👋 How can I help you today? Ask me anything about Govinda Dasa College.",
    "help": "I can help with: Admission, Fees, Courses (BCA/BBA/BCom/MBA/PUC), Placements, Exams, Sports, NSS/NCC, Library, Hostel, Scholarships, Results, Attendance, Contact info."
}



def seed_data():
    # Create default admins
    if not Admin.query.first():
        a1 = Admin(username='admin1', password=generate_password_hash('admin123', method='pbkdf2:sha256'), name='Principal')
        a2 = Admin(username='admin2', password=generate_password_hash('admin456', method='pbkdf2:sha256'), name='Vice Principal')
        db.session.add_all([a1, a2])

    # Sample fees for all branches
    if not Fee.query.first():
        fees_data = [
            ('bca', 1, 45000, 'BCA Year 1 Tuition + Exam Fee', '2024-11-30'),
            ('bca', 2, 42000, 'BCA Year 2 Tuition + Exam Fee', '2025-11-30'),
            ('bca', 3, 42000, 'BCA Year 3 Tuition + Exam Fee', '2026-11-30'),
            ('bcom', 1, 35000, 'BCom Year 1 Tuition', '2024-11-30'),
            ('bcom', 2, 33000, 'BCom Year 2 Tuition', '2025-11-30'),
            ('bba', 1, 40000, 'BBA Year 1 Tuition', '2024-11-30'),
            ('mba', 1, 80000, 'MBA Year 1 Tuition', '2024-11-30'),
            ('puc', 1, 25000, 'PUC Year 1 Tuition', '2024-11-30'),
        ]
        for b, y, amt, desc, due in fees_data:
            db.session.add(Fee(branch=b, year=y, amount=amt, description=desc, due_date=due))

    # Sample association
    if not Association.query.first():
        db.session.add(Association(name='NSS Unit', description='National Service Scheme - social service activities', category='NSS', contact='nss@gdc.edu.in'))
        db.session.add(Association(name='NCC Unit', description='National Cadet Corps - discipline and leadership', category='NCC', contact='ncc@gdc.edu.in'))
        db.session.add(Association(name='Tech Club', description='Technology and coding club for students', category='Club', event_date='2024-12-15', contact='techclub@gdc.edu.in'))

    # Sample Student
    if not Student.query.first():
        db.session.add(Student(reg_number='GDC123', name='John Doe', branch='bca', year=1, email='john@example.com', username='student1', password=generate_password_hash('student1', method='pbkdf2:sha256'), account_created=True))

    db.session.commit()
    print("✅ Database seeded with default data!")
