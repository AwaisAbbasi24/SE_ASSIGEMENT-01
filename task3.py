
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt
)

app = Flask(__name__)

# JWT Secret Key
app.config["JWT_SECRET_KEY"] = "my-secret-key-12345"

jwt = JWTManager(app)

# Users with roles
users = {
    "employee": {
        "password": "emp123",
        "role": "employee"
    },
    "admin": {
        "password": "admin123",
        "role": "admin"
    }
}

# Sample employee records
employees = [
    {"id": 1, "name": "Ali", "department": "IT"},
    {"id": 2, "name": "Sara", "department": "HR"}
]


# LOGIN API
@app.route('/login', methods=['POST'])
def login():

    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    user = users.get(username)

    if not user or user["password"] != password:
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    token = create_access_token(
        identity=username,
        additional_claims={"role": user["role"]}
    )

    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "role": user["role"]
    }), 200


# ADMIN CHECK
def admin_required():

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "error": "Administrator access required"
        }), 403

    return None


# GET ALL EMPLOYEES
@app.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():

    return jsonify(employees), 200


# ADD EMPLOYEE
@app.route('/employees', methods=['POST'])
@jwt_required()
def add_employee():

    error = admin_required()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    department = data.get("department")

    if not name or not department:
        return jsonify({
            "error": "Name and department are required"
        }), 400

    new_id = max(
        [e["id"] for e in employees],
        default=0
    ) + 1

    new_employee = {
        "id": new_id,
        "name": name,
        "department": department
    }

    employees.append(new_employee)

    return jsonify({
        "message": "Employee added successfully",
        "employee": new_employee
    }), 201


# UPDATE EMPLOYEE
@app.route('/employees/<int:id>', methods=['PUT'])
@jwt_required()
def update_employee(id):

    error = admin_required()

    if error:
        return error

    employee = next(
        (e for e in employees if e["id"] == id),
        None
    )

    if employee is None:
        return jsonify({
            "error": "Employee not found"
        }), 404

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    department = data.get("department")

    if not name or not department:
        return jsonify({
            "error": "Name and department are required"
        }), 400

    employee["name"] = name
    employee["department"] = department

    return jsonify({
        "message": "Employee updated successfully",
        "employee": employee
    }), 200


# DELETE EMPLOYEE
@app.route('/employees/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_employee(id):

    error = admin_required()

    if error:
        return error

    employee = next(
        (e for e in employees if e["id"] == id),
        None
    )

    if employee is None:
        return jsonify({
            "error": "Employee not found"
        }), 404

    employees.remove(employee)

    return jsonify({
        "message": "Employee deleted successfully"
    }), 200


# RUN APPLICATION
if __name__ == '__main__':
    app.run(debug=True, port=5002)
