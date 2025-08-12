from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import admins_collection, students_collection
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint("auth_bp", __name__)

# Register
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    role = data.get("role", "student").lower()

    # Pick the collection
    collection = admins_collection if role == "admin" else students_collection

    # Duplicate email check
    if collection.find_one({"email": data["email"]}):
        return jsonify({"error": "Email already exists"}), 400

    hashed_pw = generate_password_hash(data["password"])
    user = {
        "username": data["username"],
        "email": data["email"],
        "password": hashed_pw,
        "role": role,
        "courses": [] if role == "student" else None
    }
    collection.insert_one(user)
    return jsonify({"message": f"{role.capitalize()} registered successfully!"}), 201


# Login
@auth_bp.route("/login", methods=["GET"])
def login():
    data = request.json

    # Search in both collections
    user = admins_collection.find_one({"email": data["email"]}) \
           or students_collection.find_one({"email": data["email"]})

    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    # FIX: identity must be string
    token = create_access_token(
        identity=str(user["_id"]),  # Only string here
        additional_claims={"role": user["role"]},  # Store role separately
        expires_delta=datetime.timedelta(hours=5)
    )

    return jsonify({"token": token, "role": user["role"]})
