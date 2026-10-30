
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import date

app = Flask(__name__)
app.secret_key = "change-this-secret-before-deployment"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# Database Models
# =========================

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(30), unique=True, nullable=False)
    student_class = db.Column(db.String(50))
    department = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    attendance = db.Column(db.Float, default=0)
    internal_marks = db.Column(db.Float, default=0)
    exam_marks = db.Column(db.Float, default=0)


class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(30), default=lambda: date.today().strftime("%d-%m-%Y"))


class StudyMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500), default="")

# =========================
# Helpers
# =========================

def admin_required():
    return session.get("admin_logged_in", False)


def teacher_required():
    return session.get("teacher_logged_in", False)


def get_ai_suggestion(student):
    if student.attendance < 75:
        return "Improve your attendance and attend classes regularly."
    if student.internal_marks + student.exam_marks < 40:
        return "Focus on your studies and practise daily."
    return "Good progress! Keep learning and revising regularly."


# =========================
# Home Page
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# Admin Login / Logout
# =========================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))

        return render_template("admin_login.html", error="Invalid username or password!")

    return render_template("admin_login.html")


@app.route("/admin_dashboard")
def admin_dashboard():
    if not admin_required():
        return redirect(url_for("admin_login"))
    return render_template("admin_dashboard.html")


@app.route("/admin_logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("home"))


# =========================
# Add Student
# =========================

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if not admin_required():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        try:
            student = Student(
                name=request.form.get("name", "").strip(),
                roll_no=request.form.get("roll_no", "").strip(),
                student_class=request.form.get("student_class", "").strip(),
                department=request.form.get("department", "").strip(),
                email=request.form.get("email", "").strip(),
                phone=request.form.get("phone", "").strip(),
                attendance=float(request.form.get("attendance") or 0),
                internal_marks=float(request.form.get("internal_marks") or 0),
                exam_marks=float(request.form.get("exam_marks") or 0)
            )

            if not student.name or not student.roll_no:
                return "Name and Roll Number are required."

            if not 0 <= student.attendance <= 100:
                return "Attendance must be between 0 and 100."

            if not 0 <= student.internal_marks <= 100:
                return "Internal marks must be between 0 and 100."

            if not 0 <= student.exam_marks <= 100:
                return "Exam marks must be between 0 and 100."

            db.session.add(student)
            db.session.commit()
            return "Student saved successfully!"

        except IntegrityError:
            db.session.rollback()
            return "This Roll Number already exists."

        except ValueError:
            db.session.rollback()
            return "Please enter valid numeric values for attendance and marks."

    return render_template("add_student.html")


# =========================
# View Students
# =========================
@app.route("/students")
def students():
    if not admin_required():
        return redirect(url_for("admin_login"))

    all_students = Student.query.order_by(Student.id.desc()).all()
    return render_template("students.html", students=all_students)


# =========================
# Edit Student
# =========================

@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    student = db.get_or_404(Student, student_id)

    if request.method == "POST":
        try:
            student.name = request.form.get("name", "").strip()
            student.roll_no = request.form.get("roll_no", "").strip()
            student.student_class = request.form.get("student_class", "").strip()
            student.department = request.form.get("department", "").strip()
            student.email = request.form.get("email", "").strip()
            student.phone = request.form.get("phone", "").strip()
            student.attendance = float(request.form.get("attendance") or 0)
            student.internal_marks = float(request.form.get("internal_marks") or 0)
            student.exam_marks = float(request.form.get("exam_marks") or 0)

            if not 0 <= student.attendance <= 100:
                return "Attendance must be between 0 and 100."

            if not 0 <= student.internal_marks <= 100:
                return "Internal marks must be between 0 and 100."

            if not 0 <= student.exam_marks <= 100:
                return "Exam marks must be between 0 and 100."

            db.session.commit()
            return redirect(url_for("students"))

        except IntegrityError:
            db.session.rollback()
            return "This Roll Number already exists."

        except ValueError:
            db.session.rollback()
            return "Please enter valid numeric values."

    return render_template("edit_student.html", student=student)


# =========================
# Attendance
# =========================

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if not admin_required():
        return redirect(url_for("admin_login"))

    all_students = Student.query.order_by(Student.roll_no).all()

    if request.method == "POST":
        try:
            for student in all_students:
                value = request.form.get(f"attendance_{student.id}")
                if value is not None:
                    attendance_value = float(value)
                    if not 0 <= attendance_value <= 100:
                        return "Attendance must be between 0 and 100."
                    student.attendance = attendance_value

            db.session.commit()
            return redirect(url_for("attendance"))

        except ValueError:
            db.session.rollback()
            return "Enter valid attendance values."

    return render_template("attendance.html", students=all_students)


# =========================
# Marks
# =========================

@app.route("/update_marks/<int:id>", methods=["POST"])
def update_marks(id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    student = db.get_or_404(Student, id)

    try:
        print("Received form data:", request.form)

        internal = request.form.get("internal_marks")
        exam = request.form.get("exam_marks")

        if internal is None or exam is None:
            return "Error: Marks form madhun receive zale nahit."

        internal = float(internal)
        exam = float(exam)

        if not 0 <= internal <= 100 or not 0 <= exam <= 100:
            return "Marks 0 te 100 madhye taka."

        student.internal_marks = internal
        student.exam_marks = exam

        db.session.commit()

        print("Marks updated successfully:", student.id)
        return redirect(url_for("marks"))

    except ValueError:
        db.session.rollback()
        return "Please enter valid numeric marks."

    except Exception as e:
        db.session.rollback()
        return f"Database error: {e}"
@app.route("/marks", methods=["GET", "POST"])
def marks():
    if not admin_required():
        return redirect(url_for("admin_login"))

    all_students = Student.query.order_by(Student.roll_no).all()

    return render_template("marks.html", students=all_students)
@app.route("/notices")
def notices():
    if not admin_required() and not teacher_required():
        return redirect(url_for("home"))

    all_notices = Notice.query.order_by(Notice.id.desc()).all()
    return render_template("notices.html", notices=all_notices)
@app.route("/delete_notice/<int:id>", methods=["POST"])
def delete_notice(id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    notice = db.get_or_404(Notice, id)

    db.session.delete(notice)
    db.session.commit()

    return redirect(url_for("notices"))
    
@app.route("/add_notice", methods=["GET", "POST"])
def add_notice():
    if not admin_required():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()

        if title and message:
            notice = Notice(
                title=title,
                message=message
            )
            db.session.add(notice)
            db.session.commit()

            return redirect(url_for("notices"))

    return render_template("add_notice.html")


@app.route("/teacher/add_notice", methods=["GET", "POST"])
def teacher_add_notice():
    if not teacher_required():
        return redirect(url_for("teacher_login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()

        if title and message:
            notice = Notice(title=title, message=message)
            db.session.add(notice)
            db.session.commit()
            return redirect(url_for("notices"))

        return "Title and message are required."

    return render_template("teacher_add_notice.html")


# =========================
# Reports
# =========================

@app.route("/reports")
def reports():
    if not admin_required():
        return redirect(url_for("admin_login"))

    all_students = Student.query.all()
    return render_template("reports.html", students=all_students)


# =========================
# Teacher Login / Dashboard
# =========================

@app.route("/teacher", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "teacher" and password == "teacher123":
            session["teacher_logged_in"] = True
            return redirect(url_for("teacher_dashboard"))

        return render_template("teacher_login.html", error="Invalid username or password!")

    return render_template("teacher_login.html")


@app.route("/teacher/dashboard")
def teacher_dashboard():
    if not teacher_required():
        return redirect(url_for("teacher_login"))

    all_students = Student.query.order_by(Student.roll_no).all()
    all_notices = Notice.query.order_by(Notice.id.desc()).all()

    return render_template(
        "teacher_dashboard.html",
        students=all_students,
        notices=all_notices,
        total_students=len(all_students)
    )
    
@app.route("/teacher_logout")
def teacher_logout():
    session.pop("teacher_logged_in", None)
    return redirect(url_for("home"))


@app.route("/teacher/edit/<int:student_id>", methods=["GET", "POST"])
def teacher_edit(student_id):
    if not teacher_required():
        return redirect(url_for("teacher_login"))

    student = db.get_or_404(Student, student_id)

    if request.method == "POST":
        try:
            student.internal_marks = float(request.form.get("internal_marks") or 0)
            student.exam_marks = float(request.form.get("exam_marks") or 0)

            if not 0 <= student.internal_marks <= 100:
                return "Internal marks must be between 0 and 100."
            if not 0 <= student.exam_marks <= 100:
                return "Exam marks must be between 0 and 100."

            db.session.commit()
            return redirect(url_for("teacher_dashboard"))

        except ValueError:
            db.session.rollback()
            return "Enter valid marks."

    return render_template("teacher_edit.html", student=student)


# =========================
# Student Login / Dashboard
# =========================

@app.route("/student", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        roll_no = request.form.get("roll_no", "").strip()
        student = Student.query.filter_by(roll_no=roll_no).first()

        if student:
            session["student_id"] = student.id
            return redirect(url_for("student_dashboard"))

        return render_template("student_login.html", error="Student Roll Number not found.")

    return render_template("student_login.html")



@app.route("/student_dashboard")
def student_dashboard():
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("student_login"))

    student = db.session.get(Student, student_id)
    if not student:
        session.pop("student_id", None)
        return redirect(url_for("student_login"))

    total_marks = student.internal_marks + student.exam_marks
    percentage = total_marks / 2

    # Fetch all college notices
    all_notices = Notice.query.order_by(Notice.id.desc()).all()

    return render_template(
        "student_dashboard.html",
        student=student,
        total_marks=total_marks,
        percentage=percentage,
        ai_suggestion=get_ai_suggestion(student),
        notices=all_notices
    )


@app.route("/logout")
def logout():
    session.pop("student_id", None)
    session.pop("student_logged_in", None)
    return redirect(url_for("student_login"))


BUILT_IN_MATERIALS = [
    {
        "subject": "Python",
        "title": "Python Programming",
        "description": "Learn Python basics, variables, loops and functions.",
        "link": "https://docs.python.org/3/tutorial/"
    },
    {
        "subject": "Java",
        "title": "Java Programming",
        "description": "Learn Java syntax, classes and object-oriented programming.",
        "link": "https://dev.java/learn/"
    },
    {
        "subject": "C Programming",
        "title": "C Language",
        "description": "Learn C basics, loops, arrays and functions.",
        "link": "https://www.learn-c.org/"
    },
    {
        "subject": "C++",
        "title": "C++ Programming",
        "description": "Learn C++ syntax, classes and object-oriented concepts.",
        "link": "https://www.learncpp.com/"
    },
    {
        "subject": "SQL",
        "title": "SQL Queries",
        "description": "Learn SELECT, INSERT, UPDATE and DELETE queries.",
        "link": "https://www.w3schools.com/sql/"
    },
    {
        "subject": "DBMS",
        "title": "Database Management System",
        "description": "Learn database concepts, keys and normalization.",
        "link": "https://www.geeksforgeeks.org/dbms/"
    },
    {
        "subject": "RDBMS",
        "title": "Relational Database",
        "description": "Understand tables, relationships and constraints.",
        "link": "https://www.w3schools.com/sql/sql_intro.asp"
    },
    {
        "subject": "HTML",
        "title": "HTML Basics",
        "description": "Learn webpage structure and HTML elements.",
        "link": "https://www.w3schools.com/html/"
    },
    {
        "subject": "CSS",
        "title": "CSS Styling",
        "description": "Learn colors, layouts and responsive webpage design.",
        "link": "https://www.w3schools.com/css/"
    },
    {
        "subject": "JavaScript",
        "title": "JavaScript Basics",
        "description": "Learn variables, functions and browser interaction.",
        "link": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"
    },
    {
        "subject": "Data Structures",
        "title": "Data Structures",
        "description": "Learn arrays, stacks, queues, trees and linked lists.",
        "link": "https://www.geeksforgeeks.org/data-structures/"
    },
    {
        "subject": "Algorithms",
        "title": "Algorithms",
        "description": "Learn searching, sorting and algorithm fundamentals.",
        "link": "https://www.geeksforgeeks.org/fundamentals-of-algorithms/"
    },
    {
        "subject": "Machine Learning",
        "title": "Machine Learning Basics",
        "description": "Understand machine learning concepts and models.",
        "link": "https://www.ibm.com/think/topics/machine-learning"
    },
    {
        "subject": "Artificial Intelligence",
        "title": "Introduction to AI",
        "description": "Explore artificial intelligence and its applications.",
        "link": "https://www.ibm.com/think/topics/artificial-intelligence"
    },
    {
        "subject": "Deep Learning",
        "title": "Deep Learning Basics",
        "description": "Learn neural networks and deep learning concepts.",
        "link": "https://www.ibm.com/think/topics/deep-learning"
    },
    {
        "subject": "Computer Networks",
        "title": "Networking Fundamentals",
        "description": "Learn network types, protocols and communication.",
        "link": "https://www.geeksforgeeks.org/computer-network-tutorials/"
    },
    {
        "subject": "Operating System",
        "title": "Operating System Basics",
        "description": "Learn processes, memory and file management.",
        "link": "https://www.geeksforgeeks.org/operating-systems/"
    },
    {
        "subject": "Software Engineering",
        "title": "Software Engineering",
        "description": "Learn SDLC, software testing and development models.",
        "link": "https://www.geeksforgeeks.org/software-engineering/"
    },
    {
        "subject": "Flask",
        "title": "Flask Web Development",
        "description": "Learn Python Flask routes, templates and forms.",
        "link": "https://flask.palletsprojects.com/en/stable/tutorial/"
    },
    {
        "subject": "Django",
        "title": "Django Web Development",
        "description": "Learn Django models, views and templates.",
        "link": "https://docs.djangoproject.com/en/stable/intro/tutorial01/"
    },
    {
        "subject": "Git and GitHub",
        "title": "Version Control",
        "description": "Learn repositories, commits and version control.",
        "link": "https://docs.github.com/en/get-started"
    },
    {
        "subject": "Computer Fundamentals",
        "title": "Computer Basics",
        "description": "Learn hardware, software and basic computer concepts.",
        "link": "https://edu.gcfglobal.org/en/computerbasics/"
    },
    {
        "subject": "OOP",
        "title": "Object-Oriented Programming",
        "description": "Learn classes, objects, inheritance and polymorphism.",
        "link": "https://www.geeksforgeeks.org/object-oriented-programming-oops-concept-in-java/"
    },
    {
        "subject": "Cyber Security",
        "title": "Cyber Security Basics",
        "description": "Learn security fundamentals and online safety.",
        "link": "https://www.cisa.gov/topics/cybersecurity-best-practices"
    },
    {
        "subject": "Data Science",
        "title": "Introduction to Data Science",
        "description": "Learn data analysis and data science fundamentals.",
        "link": "https://www.ibm.com/think/topics/data-science"
    }
]


@app.route("/student_logout")
def student_logout():
    session.pop("student_id", None)
    return redirect(url_for("home"))

# ================= STUDENT STUDY MATERIAL =================




@app.route("/student/study-material")
def student_study_material():
    if not session.get("student_id"):
        return redirect(url_for("student_login"))

    search = request.args.get("q", "").strip().lower()

    # Built-in materials
    all_materials = list(BUILT_IN_MATERIALS)

    # Admin-added database materials
    saved_materials = StudyMaterial.query.order_by(
        StudyMaterial.id.desc()
    ).all()

    for item in saved_materials:
        # Avoid duplicate Python subject (case-insensitive)
        if item.subject.strip().lower() == "python":
            continue

        all_materials.append({
            "subject": item.subject,
            "title": item.title,
            "description": item.description,
            "link": item.link or ""
        })

    # Unique subject list (case-insensitive)
    # Unique subject list (case-insensitive)
    subject_map = {}

    for item in all_materials:
        key = item["subject"].strip().lower()

        if key not in subject_map:
            subject_map[key] = item["subject"].strip()

    subjects = sorted(subject_map.values(), key=str.lower)

    if search:
        materials = [
            item for item in all_materials
            if search in item["subject"].lower()
            or search in item["title"].lower()
            or search in item["description"].lower()
        ]
    else:
        materials = all_materials

    print("TOTAL SUBJECTS:", len(subjects))
    print("SUBJECT LIST:", subjects)

    return render_template(
        "student_study_material.html",
        materials=materials,
        subjects=subjects,
        search=search
    )
 # ================= ADMIN STUDY MATERIAL =================

@app.route("/study_material")
def study_material_redirect():
    return redirect(url_for("admin_study_material"))

@app.route("/admin/study-material", methods=["GET", "POST"])
def admin_study_material():
    if not admin_required():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        link = request.form.get("link", "").strip()

        if not subject or not title or not description:
            return "Subject, Title and Description are required."

        material = StudyMaterial(
            subject=subject,
            title=title,
            description=description,
            link=link
        )

        db.session.add(material)
        db.session.commit()

        return redirect(url_for("admin_study_material"))

    search = request.args.get("q", "").strip().lower()

    all_materials = list(BUILT_IN_MATERIALS)

    saved_materials = StudyMaterial.query.order_by(
        StudyMaterial.id.desc()
    ).all()

    for item in saved_materials:
        all_materials.append({
            "subject": item.subject,
            "title": item.title,
            "description": item.description,
            "link": item.link or ""
        })

    subject_map = {}

    for item in all_materials:
        key = item["subject"].strip().lower()

        if key not in subject_map:
            subject_map[key] = item["subject"].strip()

    subjects = sorted(subject_map.values(), key=str.lower)

    if search:
        materials = [
            item for item in all_materials
            if search in item["subject"].strip().lower()
        ]
    else:
        materials = all_materials

    return render_template(
        "admin_study_material.html",
        materials=materials,
        subjects=subjects,
        search=search
    )

# =========================
# Database Setup
# =========================

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)