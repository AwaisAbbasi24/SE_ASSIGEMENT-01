
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "students.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()


# GET all students
@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()
    conn.close()

    return jsonify([dict(s) for s in students]), 200


# GET a specific student
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student)), 200


# POST a new student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json(silent=True) or {}

    name = data.get('name')
    department = data.get('department')
    email = data.get('email')

    if not all([name, department, email]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            "INSERT INTO students (name, department, email) VALUES (?, ?, ?)",
            (name, department, email)
        )
        conn.commit()
        student_id = cursor.lastrowid

        return jsonify({
            "message": "Student added successfully",
            "id": student_id
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409

    finally:
        conn.close()


# PUT update student
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True) or {}

    name = data.get('name')
    department = data.get('department')
    email = data.get('email')

    if not all([name, department, email]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            UPDATE students
            SET name = ?, department = ?, email = ?
            WHERE id = ?
        """, (name, department, email, id))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student updated successfully"}), 200

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409

    finally:
        conn.close()


# DELETE student
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()

    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?", (id,)
    )

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"}), 200


if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, port=5000)
