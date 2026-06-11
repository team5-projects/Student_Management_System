from flask import Flask, render_template, request, redirect, session

from services.student_service import (
    add_student,
    remove_student,
    get_all_students,
    get_student,
    get_attendance_by_roll,
    student_exists,
    get_student_by_roll
)

from services.marks_service import add_marks
from services.attendance_service import mark_attendance, undo_attendance_by_roll
from services.relationship_service import add_relationship, get_relationships, get_relationship_details


app = Flask(__name__)
app.secret_key = "secret123"

TEACHER_PASSWORD = "admin123"


# Home page
@app.route('/')
def index():
    return render_template("index.html")


# Teacher login
@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():

    if request.method == "POST":
        password = request.form.get("password")

        if password == TEACHER_PASSWORD:
            session["teacher"] = True
            return redirect("/teacher_dashboard")
        else:
            return render_template(
                "teacher_login.html",
                error="Wrong password"
            )

    return render_template("teacher_login.html")


# Teacher dashboard
@app.route('/teacher_dashboard')
def teacher_dashboard():

    if "teacher" not in session:
        return redirect("/")

    return render_template("teacher_dashboard.html")


# Add student
@app.route('/add_student', methods=["GET", "POST"])
def add_student_route():

    if request.method == "POST":
        add_student(
            request.form["name"],
            request.form["roll_no"]
        )

    return render_template("add_student.html")


# Remove student
@app.route('/remove_student', methods=["GET", "POST"])
def remove_student_route():

    if request.method == "POST":
        remove_student(request.form["roll_no"])

    return render_template("remove_student.html")


# Enter marks
@app.route('/enter_marks', methods=["GET", "POST"])
def enter_marks_route():

    if request.method == "POST":
        add_marks(
            request.form["roll_no"],
            int(request.form["s1"]),
            int(request.form["s2"]),
            int(request.form["s3"]),
            int(request.form["s4"]),
            int(request.form["s5"])
        )

    return render_template("enter_marks.html")


# Mark attendance
@app.route('/mark_attendance', methods=["GET", "POST"])
def mark_attendance_route():

    if request.method == "POST":
        mark_attendance(
            request.form["roll_no"],
            request.form["status"]
        )

    return render_template("mark_attendance.html")


# Undo attendance
@app.route('/undo_attendance', methods=["GET", "POST"])
def undo_attendance_route():

    if request.method == "POST":
        roll_no = request.form.get("roll_no")
        undo_attendance_by_roll(roll_no)

    return render_template("undo_attendance.html")


# View all students
@app.route('/view_students')
def view_students():

    students = get_all_students()
    return render_template("view_students.html", students=students)


# View student relationships (teacher)
@app.route("/view_relationships_teacher", methods=["GET", "POST"])
def view_relationships_teacher():

    relations = []
    roll_no = None

    if request.method == "POST":
        roll_no = request.form["roll_no"]

        friend_rolls = get_relationships(roll_no)

        for r in friend_rolls:
            student = get_student_by_roll(r)

            if student:
                relations.append({
                    "name": student["name"],
                    "roll_no": r
                })

    return render_template(
        "view_relationships_teacher.html",
        relations=relations,
        roll_no=roll_no
    )


# Student relationships
@app.route("/student_relationships")
def student_relationships():

    roll_no = session.get("roll_no")
    relations = get_relationship_details(roll_no)

    return render_template(
        "student_relationships.html",
        relations=relations
    )


# Add friend
@app.route("/add_friend", methods=["GET", "POST"])
def add_friend():

    roll_no = session.get("roll_no")

    if request.method == "POST":
        friend = request.form.get("friend_roll")

        if friend != roll_no:
            add_relationship(roll_no, friend)

    return render_template("add_friend.html")


# Student login
@app.route("/student_login", methods=["GET", "POST"])
def student_login():

    error = None

    if request.method == "POST":
        roll_no = request.form.get("roll_no")

        if not student_exists(roll_no):
            error = "Student does not exist"
        else:
            session["roll_no"] = roll_no
            return redirect("/student_dashboard")

    return render_template("student_login.html", error=error)


# Student dashboard
@app.route('/student_dashboard')
def student_dashboard():
    return render_template("student_dashboard.html")


# View marks
@app.route('/view_marks')
def view_marks():

    student = get_student(session["roll_no"])
    return render_template("view_marks.html", data=student)


# View attendance
@app.route("/view_attendance")
def view_attendance():

    roll_no = session.get("roll_no")
    attendance = get_attendance_by_roll(roll_no)

    present_count = attendance.count("Present")
    absent_count = attendance.count("Absent")

    return render_template(
        "view_attendance.html",
        data=attendance,
        present_count=present_count,
        absent_count=absent_count
    )


# Logout
@app.route('/logout')
def logout():

    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
