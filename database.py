# ==============================
# database.py
# ==============================

import sqlite3

# ------------------------------
# Database connect function
# ------------------------------
def connect():
    return sqlite3.connect("quiz.db")


# ------------------------------
# All tables create function
# ------------------------------
def create_tables():

    conn = connect()
    cur = conn.cursor()

    # ===== Admin Table =====
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # ===== Category Table =====
    cur.execute("""
    CREATE TABLE IF NOT EXISTS category(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    # ===== Quiz Table =====
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quiz(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        category_id INTEGER
    )
    """)

    # ===== Question Table =====
    cur.execute("""
    CREATE TABLE IF NOT EXISTS question(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER,
        question TEXT,
        option1 TEXT,
        option2 TEXT,
        option3 TEXT,
        option4 TEXT,
        correct_option INTEGER,
        marks INTEGER
    )
    """)

    conn.commit()
    conn.close()