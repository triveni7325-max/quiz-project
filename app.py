from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from database import create_tables

app = Flask(__name__)
app.secret_key = "secretkey"

# Create tables automatically
create_tables()


# ==============================
# Database Connection
# ==============================
def get_db():
    conn = sqlite3.connect("quiz.db")
    conn.row_factory = sqlite3.Row
    return conn


# ==============================
# Admin Login
# ==============================
@app.route("/", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if admin:
            session["admin"] = admin["username"]
            return redirect("/dashboard")
        else:
            return "Invalid Username or Password"

    return render_template("admin_login.html")


# ==============================
# Dashboard
# ==============================
@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/")

    return render_template("dashboard.html")


# ==============================
# Logout
# ==============================
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")


# ==============================
# Category Page
# ==============================
@app.route("/category", methods=["GET", "POST"])
def category():

    if "admin" not in session:
        return redirect("/")

    conn = get_db()

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        conn.execute(
            "INSERT INTO category (name, description) VALUES (?,?)",
            (name, description)
        )
        conn.commit()

    categories = conn.execute("SELECT * FROM category").fetchall()
    conn.close()

    return render_template("category.html", categories=categories)


# ==============================
# Quiz Page
# ==============================
@app.route("/quiz/<int:category_id>", methods=["GET", "POST"])
def quiz(category_id):

    if "admin" not in session:
        return redirect("/")

    conn = get_db()

    category = conn.execute(
        "SELECT * FROM category WHERE id=?",
        (category_id,)
    ).fetchone()

    if request.method == "POST":
        title = request.form["title"]
        total_time = request.form["total_time"]

        conn.execute("""
            INSERT INTO quiz (category_id, title, total_time)
            VALUES (?, ?, ?)
        """, (category_id, title, total_time))
        conn.commit()

    quizzes = conn.execute("""
        SELECT 
            q.id,
            q.title,
            q.total_time,
            COUNT(que.id) AS total_question,
            IFNULL(SUM(que.marks),0) AS total_marks
        FROM quiz q
        LEFT JOIN question que ON q.id = que.quiz_id
        WHERE q.category_id=?
        GROUP BY q.id
    """, (category_id,)).fetchall()

    conn.close()

    return render_template("quiz.html", category=category, quizzes=quizzes)


# ==============================
# Question Page
# ==============================
@app.route("/question/<int:quiz_id>", methods=["GET", "POST"])
def question(quiz_id):

    if "admin" not in session:
        return redirect("/")

    conn = get_db()

    quiz = conn.execute(
        "SELECT * FROM quiz WHERE id=?",
        (quiz_id,)
    ).fetchone()

    if request.method == "POST":

        conn.execute("""
            INSERT INTO question
            (quiz_id, question, option1, option2, option3, option4, correct_option, marks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quiz_id,
            request.form["question"],
            request.form["option1"],
            request.form["option2"],
            request.form["option3"],
            request.form["option4"],
            request.form["correct_option"],
            request.form["marks"]
        ))
        conn.commit()

    questions = conn.execute(
        "SELECT * FROM question WHERE quiz_id=?",
        (quiz_id,)
    ).fetchall()

    conn.close()

    return render_template("question.html", quiz=quiz, questions=questions)


# ==============================
# Delete Question (AJAX)
# ==============================
@app.route("/delete_question/<int:id>", methods=["DELETE"])
def delete_question(id):

    conn = get_db()
    conn.execute("DELETE FROM question WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ==============================
# Edit Question
# ==============================
@app.route("/edit_question/<int:id>", methods=["GET", "POST"])
def edit_question(id):

    if "admin" not in session:
        return redirect("/")

    conn = get_db()

    question = conn.execute(
        "SELECT * FROM question WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        conn.execute("""
            UPDATE question SET
            question=?,
            option1=?,
            option2=?,
            option3=?,
            option4=?,
            correct_option=?,
            marks=?
            WHERE id=?
        """, (
            request.form["question"],
            request.form["option1"],
            request.form["option2"],
            request.form["option3"],
            request.form["option4"],
            request.form["correct_option"],
            request.form["marks"],
            id
        ))

        conn.commit()
        conn.close()

        return redirect(f"/question/{question['quiz_id']}")

    conn.close()
    return render_template("edit_question.html", question=question)


if __name__ == "__main__":
    app.run(debug=True)