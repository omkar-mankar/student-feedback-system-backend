from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import admins_collection, students_collection
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint("auth_bp", __name__)

# ---------------------------
# Register
# ---------------------------
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


# ---------------------------
# Login (sets cookies)
# ---------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    # Search in both collections
    user = admins_collection.find_one({"email": data["email"]}) \
           or students_collection.find_one({"email": data["email"]})

    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(
        identity=str(user["_id"]),  # identity must be string
        additional_claims={"role": user["role"], "username": user["username"]},
        expires_delta=datetime.timedelta(hours=5)
    )

    # Send JWT + set cookies
    response = jsonify({
        "message": "Login successful",
        "token": token,
        "role": user["role"],
        "username": user["username"]  # added username here
    })
    response.set_cookie("user_id", str(user["_id"]))
    response.set_cookie("role", user["role"])
    response.set_cookie("username", user["username"])  # optional cookie
    return response
