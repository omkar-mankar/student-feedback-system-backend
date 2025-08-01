from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import users_collection
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint("auth_bp", __name__)

# Register (Student by default)
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"error": "Email already exists"}), 400

    hashed_pw = generate_password_hash(data["password"])
    user = {
        "username": data["username"],
        "email": data["email"],
        "password": hashed_pw,
        "role": data.get("role", "student"),  # default is student
        "courses": []  # Only for students
    }
    users_collection.insert_one(user)
    return jsonify({"message": "User registered successfully!"}), 201


# Login (Student/Admin)
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = users_collection.find_one({"email": data["email"]})
    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(
        identity={"id": str(user["_id"]), "role": user["role"]},
        expires_delta=datetime.timedelta(hours=5)
    )
    return jsonify({"token": token, "role": user["role"]})