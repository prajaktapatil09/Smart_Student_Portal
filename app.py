
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

@app.route("/marks", methods=["GET", "POST"])
def marks():
    if not admin_required():
        return redirect(url_for("admin_login"))

    all_students = Student.query.order_by(Student.roll_no).all()

    if request.method == "POST":
        try:
            for student in all_students:
                internal = request.form.get(f"internal_{student.id}")
                exam = request.form.get(f"exam_{student.id}")

                if internal is not None:
                    student.internal_marks = float(internal)
                if exam is not None:
                    student.exam_marks = float(exam)

                if not 0 <= student.internal_marks <= 100:
                    return "Internal marks must be between 0 and 100."
                if not 0 <= student.exam_marks <= 100:
                    return "Exam marks must be between 0 and 100."

            db.session.commit()
            return redirect(url_for("marks"))

        except ValueError:
            db.session.rollback()
            return "Enter valid marks."

    return render_template("marks.html", students=all_students)


# =========================
# Notices
# =========================

@app.route("/notices")
def notices():
    if not admin_required() and not teacher_required():
        return redirect(url_for("home"))

    all_notices = Notice.query.order_by(Notice.id.desc()).all()
    return render_template("notices.html", notices=all_notices)


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


@app.route("/teacher_dashboard")
def teacher_dashboard():
    if not teacher_required():
        return redirect(url_for("teacher_login"))
    return render_template("teacher_dashboard.html")


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

    return render_template(
        "student_dashboard.html",
        student=student,
        total_marks=total_marks,
        percentage=percentage,
        ai_suggestion=get_ai_suggestion(student)
    )


@app.route("/student/study-material")
def student_study_material():
    if not session.get("student_id"):
        return redirect(url_for("student_login"))

    return render_template("student_study_material.html")


@app.route("/student_logout")
def student_logout():
    session.pop("student_id", None)
    return redirect(url_for("home"))


# =========================
# Database Setup
# =========================

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
