import sqlite3
from contextlib import contextmanager
from pathlib import Path

from flask import Flask, jsonify, request, send_file


app = Flask(__name__)
DATABASE = Path(__file__).with_name("employees.db")


@contextmanager
def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                department TEXT NOT NULL,
                role TEXT NOT NULL,
                phone TEXT NOT NULL,
                joined_date TEXT NOT NULL
            )
            """
        )


def employee_from_row(row):
    return dict(row)


def validate_employee(payload):
    fields = ("name", "email", "department", "role", "phone", "joined_date")
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."

    missing = [field for field in fields if not str(payload.get(field, "")).strip()]
    if missing:
        return "Required fields missing: " + ", ".join(missing)
    return None


@app.route("/")
def home():
    return send_file(Path(__file__).with_name("index.html"))


@app.route("/api/employees", methods=["GET"])
def list_employees():
    search = request.args.get("search", "").strip()
    with get_connection() as connection:
        if search:
            pattern = f"%{search}%"
            rows = connection.execute(
                """
                SELECT * FROM employees
                WHERE name LIKE ? OR email LIKE ? OR department LIKE ? OR role LIKE ?
                ORDER BY id DESC
                """,
                (pattern, pattern, pattern, pattern),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM employees ORDER BY id DESC"
            ).fetchall()
    return jsonify([employee_from_row(row) for row in rows])


@app.route("/api/employees", methods=["POST"])
def create_employee():
    payload = request.get_json(silent=True)
    error = validate_employee(payload)
    if error:
        return jsonify({"error": error}), 400

    values = tuple(str(payload[field]).strip() for field in
                   ("name", "email", "department", "role", "phone", "joined_date"))
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO employees (name, email, department, role, phone, joined_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            row = connection.execute(
                "SELECT * FROM employees WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
    except sqlite3.IntegrityError:
        return jsonify({"error": "An employee with this email already exists."}), 409

    return jsonify(employee_from_row(row)), 201


@app.route("/api/employees/<int:employee_id>", methods=["GET", "PUT", "DELETE"])
def employee_detail(employee_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM employees WHERE id = ?", (employee_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "Employee not found."}), 404

        if request.method == "GET":
            return jsonify(employee_from_row(row))

        if request.method == "DELETE":
            connection.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
            return jsonify({"message": "Employee deleted successfully."})

        payload = request.get_json(silent=True)
        error = validate_employee(payload)
        if error:
            return jsonify({"error": error}), 400
        values = tuple(str(payload[field]).strip() for field in
                       ("name", "email", "department", "role", "phone", "joined_date"))
        try:
            connection.execute(
                """
                UPDATE employees
                SET name = ?, email = ?, department = ?, role = ?, phone = ?, joined_date = ?
                WHERE id = ?
                """,
                values + (employee_id,),
            )
        except sqlite3.IntegrityError:
            return jsonify({"error": "An employee with this email already exists."}), 409
        updated = connection.execute(
            "SELECT * FROM employees WHERE id = ?", (employee_id,)
        ).fetchone()
    return jsonify(employee_from_row(updated))


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Resource not found."}), 404
    return error


initialize_database()


if __name__ == "__main__":
    app.run(debug=True)