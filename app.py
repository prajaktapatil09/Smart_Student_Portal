from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.secret_key = "smart_student_secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# Student Model
# =========================
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    student_class = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    attendance = db.Column(db.Float, default=0)
    internal_marks = db.Column(db.Float, default=0)
    exam_marks = db.Column(db.Float, default=0)
class StudyMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500))
BUILT_IN_MATERIALS = [
    {
        "subject": "Python",
        "title": "Python Functions",
        "description": "Learn functions, parameters and return values.",
        "link": "https://www.w3schools.com/python/python_functions.asp"
    },
    {
        "subject": "Python",
        "title": "Python Lists and Tuples",
        "description": "Learn Python lists, tuples and their related functions.",
        "link": "https://www.w3schools.com/python/python_lists.asp"
    },
    {
        "subject": "SQL",
        "title": "SQL SELECT and WHERE",
        "description": "Learn SELECT, WHERE and ORDER BY queries.",
        "link": "https://www.w3schools.com/sql/"
    },
    {
        "subject": "Java",
        "title": "Java Class and Object",
        "description": "Learn classes, objects and basic Java programming.",
        "link": "https://www.w3schools.com/java/"
    },
    {
        "subject": "Machine Learning",
        "title": "Machine Learning Basics",
        "description": "Learn supervised learning, classification and regression.",
        "link": "https://www.ibm.com/think/topics/machine-learning"
    },
    {
        "subject": "C Programming",
        "title": "C Programming Basics",
        "description": "Learn variables, data types, operators and basic C programs.",
        "link": "https://www.w3schools.com/c/"
    },
    {
        "subject": "C++",
        "title": "C++ Programming",
        "description": "Learn C++ syntax, classes, objects and basic programming.",
        "link": "https://www.w3schools.com/cpp/"
    },
    {
        "subject": "HTML",
        "title": "HTML Basics",
        "description": "Learn HTML tags, headings, links, tables and forms.",
        "link": "https://www.w3schools.com/html/"
    },
    {
        "subject": "CSS",
        "title": "CSS Basics",
        "description": "Learn CSS selectors, properties, layouts and styling.",
        "link": "https://www.w3schools.com/css/"
    },
    {
        "subject": "JavaScript",
        "title": "JavaScript Basics",
        "description": "Learn variables, functions, conditions and JavaScript basics.",
        "link": "https://www.w3schools.com/js/"
    },
    {
        "subject": "DBMS",
        "title": "DBMS Basics",
        "description": "Learn database concepts, tables, keys and relationships.",
        "link": "https://www.w3schools.com/sql/"
    },
    {
        "subject": "RDBMS",
        "title": "RDBMS and SQL",
        "description": "Learn relational databases, SQL queries and constraints.",
        "link": "https://www.w3schools.com/sql/"
    },
    {
        "subject": "Data Structures",
        "title": "Data Structures Basics",
        "description": "Learn arrays, stacks, queues, linked lists and trees.",
        "link": "https://www.geeksforgeeks.org/data-structures/"
    },
    {
        "subject": "Artificial Intelligence",
        "title": "Artificial Intelligence Basics",
        "description": "Learn AI concepts, applications and intelligent systems.",
        "link": "https://www.ibm.com/think/topics/artificial-intelligence"
    },
    {
        "subject": "Deep Learning",
        "title": "Deep Learning Basics",
        "description": "Learn neural networks and basic deep learning concepts.",
        "link": "https://www.ibm.com/think/topics/deep-learning"
    },
    {
        "subject": "Computer Networks",
        "title": "Computer Networks Basics",
        "description": "Learn networking concepts, protocols and network devices.",
        "link": "https://www.geeksforgeeks.org/computer-network-tutorials/"
    },
    {
        "subject": "Operating System",
        "title": "Operating System Basics",
        "description": "Learn processes, memory management and file systems.",
        "link": "https://www.geeksforgeeks.org/operating-systems/"
    },
    {
        "subject": "Software Engineering",
        "title": "Software Engineering Basics",
        "description": "Learn software development life cycle and software processes.",
        "link": "https://www.geeksforgeeks.org/software-engineering/"
    },
    {
        "subject": "Flask",
        "title": "Python Flask",
        "description": "Learn Flask routes, templates and web application development.",
        "link": "https://flask.palletsprojects.com/"
    },
    {
        "subject": "GitHub",
        "title": "GitHub Basics",
        "description": "Learn repositories, commits, branches and uploading projects.",
        "link": "https://docs.github.com/en/get-started"
    },
    {
        "subject": "Python",
        "title": "Python Conditional Statements",
        "description": "Learn if, elif and else statements in Python.",
        "link": "https://www.w3schools.com/python/python_conditions.asp"
    },
    {
        "subject": "Python",
        "title": "Python Loops",
        "description": "Learn for loops, while loops and loop control statements.",
        "link": "https://www.w3schools.com/python/python_for_loops.asp"
    },
    {
        "subject": "SQL",
        "title": "SQL INSERT UPDATE DELETE",
        "description": "Learn INSERT, UPDATE and DELETE SQL commands.",
        "link": "https://www.w3schools.com/sql/sql_insert.asp"
    },
    {
        "subject": "Java",
        "title": "Java Inheritance",
        "description": "Learn inheritance and its use in Java programming.",
        "link": "https://www.w3schools.com/java/java_inheritance.asp"
    }
]
def get_ai_suggestion(student):
    total = student.internal_marks + student.exam_marks

    if student.attendance < 75 and total < 40:
        return "Attendance is low and marks need improvement. Focus on regular attendance and studies."

    elif student.attendance < 75:
        return "Improve your attendance by attending classes regularly."

    elif total < 40:
        return "Marks need improvement. Focus more on your studies and practice."

    elif total >= 80 and student.attendance >= 75:
        return "Excellent performance! Keep up the good work."

    else:
        return "Good progress. Continue studying regularly to improve further."
@app.route("/study_material", methods=["GET", "POST"])
def study_material():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        material = StudyMaterial(
            subject=request.form.get("subject"),
            title=request.form.get("title"),
            description=request.form.get("description"),
            link=request.form.get("link")
        )

        db.session.add(material)
        db.session.commit()

        return redirect(url_for("study_material"))

    materials = StudyMaterial.query.order_by(
        StudyMaterial.id.desc()
    ).all()

    return render_template(
        "study_material.html",
        materials=materials
    )

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50), nullable=False)

# =========================
# Home Page
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# Admin Login
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))

        return "Invalid username or password!"

    return render_template("admin_login.html")
@app.route("/student", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        roll_no = request.form.get("roll_no")

        student = Student.query.filter_by(
            roll_no=roll_no
        ).first()

        if student:
            session["student_id"] = student.id
            return redirect(url_for("student_dashboard"))

        return "Student not found! Please check your Roll Number."

    return render_template("student_login.html")
@app.route("/teacher", methods=["GET", "POST"])
def teacher_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "teacher" and password == "teacher123":
            session["teacher_logged_in"] = True
            return redirect(url_for("teacher_dashboard"))

        return "Invalid username or password!"

    return render_template("teacher_login.html")
@app.route("/teacher/dashboard")
def teacher_dashboard():

    if not session.get("teacher_logged_in"):
        return redirect(url_for("teacher_login"))

    students = Student.query.all()
    notices = Notice.query.order_by(Notice.id.desc()).all()

    return render_template(
        "teacher_dashboard.html",
        students=students,
        notices=notices
    )
@app.route("/teacher/edit/<int:id>", methods=["GET", "POST"])
def teacher_edit_student(id):

    if not session.get("teacher_logged_in"):
        return redirect(url_for("teacher_login"))

    student = Student.query.get_or_404(id)

    if request.method == "POST":

        student.attendance = float(
            request.form.get("attendance") or 0
        )

        student.internal_marks = float(
            request.form.get("internal_marks") or 0
        )

        student.exam_marks = float(
            request.form.get("exam_marks") or 0
        )

        db.session.commit()

        return redirect(url_for("teacher_dashboard"))

    return render_template(
        "teacher_edit.html",
        student=student
    )
@app.route("/teacher/search")
def teacher_search():

    if not session.get("teacher_logged_in"):
        return redirect(url_for("teacher_login"))

    search = request.args.get("q", "")

    students = Student.query.filter(
        (Student.name.ilike(f"%{search}%")) |
        (Student.roll_no.ilike(f"%{search}%"))
    ).all()

    return render_template(
        "teacher_dashboard.html",
        students=students,
        search=search
    )
@app.route("/student/dashboard")
def student_dashboard():

    if not session.get("student_id"):
        return redirect(url_for("student_login"))

    student = Student.query.get_or_404(
        session["student_id"]
    )

    notices = Notice.query.order_by(
        Notice.id.desc()
    ).all()

    ai_suggestion = get_ai_suggestion(student)

    return render_template(
        "student_dashboard.html",
        student=student,
        notices=notices,
        ai_suggestion=ai_suggestion
    )

# =========================
# Adminashboard
# =========================
@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    students = Student.query.all()

    print("ADMIN DASHBOARD ROUTE WORKING")

    return render_template(
        "admin_dashboard.html",
        students=students
    )


# =========================
# Add Student
# =========================
@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        student = Student(
            name=request.form.get("name"),
            roll_no=request.form.get("roll_no"),
            student_class=request.form.get("student_class"),
            department=request.form.get("department"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            attendance=float(request.form.get("attendance") or 0),
            internal_marks=float(request.form.get("internal_marks") or 0),
            exam_marks=float(request.form.get("exam_marks") or 0)
        )

        try:
            db.session.add(student)
            db.session.commit()

            return redirect(url_for("students"))

        except IntegrityError:
            db.session.rollback()

            return """
            <h2>Roll Number already exists!</h2>
            <p>Please enter a different Roll Number.</p>
            <a href="/add_student">Try Again</a>
            """

    return render_template("add_student.html")

@app.route("/attendance")
def attendance():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    students = Student.query.all()

    return render_template(
        "attendance.html",
        students=students
    )

@app.route("/marks")
def marks():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    students = Student.query.all()

    return render_template(
        "marks.html",
        students=students
    )
@app.route("/notices", methods=["GET", "POST"])
def notices():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form.get("title")
        message = request.form.get("message")

        from datetime import datetime

        notice = Notice(
            title=title,
            message=message,
            date=datetime.now().strftime("%d-%m-%Y")
        )

        db.session.add(notice)
        db.session.commit()

        return redirect(url_for("notices"))

    all_notices = Notice.query.order_by(Notice.id.desc()).all()

    return render_template(
        "notices.html",
        notices=all_notices
    )

@app.route("/delete_notice/<int:id>", methods=["POST"])
def delete_notice(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    notice = Notice.query.get_or_404(id)

    db.session.delete(notice)
    db.session.commit()

    return redirect(url_for("notices"))
@app.route("/reports")
def reports():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    students = Student.query.order_by(Student.roll_no).all()

    return render_template(
        "reports.html",
        students=students
    )

@app.route("/update_marks/<int:id>", methods=["POST"])
def update_marks(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    student = Student.query.get_or_404(id)

    student.internal_marks = float(request.form.get("internal_marks") or 0)
    student.exam_marks = float(request.form.get("exam_marks") or 0)

    db.session.commit()

    return redirect(url_for("marks"))
# =========================
# View Students
# =========================
@app.route("/students")
def students():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    all_students = Student.query.all()

    return render_template(
        "students.html",
        students=all_students
    )


# =========================
# Search Student
# =========================
@app.route("/search")
def search_student():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    search = request.args.get("q", "")

    results = Student.query.filter(
        (Student.name.ilike(f"%{search}%")) |
        (Student.roll_no.ilike(f"%{search}%"))
    ).all()

    return render_template(
        "students.html",
        students=results,
        search=search
    )


# =========================
# Edit Student
# =========================
@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    student = Student.query.get_or_404(id)

    if request.method == "POST":

        student.name = request.form.get("name")
        student.roll_no = request.form.get("roll_no")
        student.student_class = request.form.get("student_class")
        student.department = request.form.get("department")
        student.email = request.form.get("email")
        student.phone = request.form.get("phone")

        student.attendance = float(
            request.form.get("attendance") or 0
        )

        student.internal_marks = float(
            request.form.get("internal_marks") or 0
        )

        student.exam_marks = float(
            request.form.get("exam_marks") or 0
        )

        try:
            db.session.commit()

            return redirect(url_for("students"))

        except IntegrityError:
            db.session.rollback()

            return """
            <h2>Roll Number already exists!</h2>
            <p>Please use another Roll Number.</p>
            <a href="/students">Back to Students</a>
            """

    return render_template(
        "edit_student.html",
        student=student
    )


# =========================
# Delete Student
# =========================
@app.route("/delete_student/<int:id>", methods=["POST"])
def delete_student(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    student = Student.query.get_or_404(id)

    db.session.delete(student)
    db.session.commit()

    return redirect(url_for("students"))


# =========================
# Logout
# =========================
@app.route("/logout")
def logout():

    session.pop("admin_logged_in", None)

    return redirect(url_for("home"))


# =========================
# Create Database
# =========================
with app.app_context():
    db.create_all()


# =========================
# Run Application
@app.route("/student/study-material")
def student_study_material():

    if not session.get("student_id"):
        return redirect(url_for("student_login"))

    search = request.args.get("q", "").strip().lower()

    if search:
        materials = [
            material for material in BUILT_IN_MATERIALS
            if search in material["subject"].lower()
            or search in material["title"].lower()
            or search in material["description"].lower()
        ]
    else:
        materials = BUILT_IN_MATERIALS

    return render_template(
        "student_study_material.html",
        materials=materials,
        search=search
    )
@app.route("/teacher/add-notice", methods=["GET", "POST"])
def teacher_add_notice():

    if not session.get("teacher_logged_in"):
        return redirect(url_for("teacher_login"))

    if request.method == "POST":

        notice = Notice(
            title=request.form.get("title"),
            message=request.form.get("message"),
            date=request.form.get("date")
        )

        db.session.add(notice)
        db.session.commit()

        return redirect(url_for("teacher_add_notice"))

    notices = Notice.query.order_by(
        Notice.id.desc()
    ).all()

    return render_template(
        "teacher_add_notice.html",
        notices=notices
    )
# =========================
if __name__ == "__main__":
    app.run(debug=True)