from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from models.user_model import users_collection
from models.course_model import courses_collection
from bson import ObjectId

student_bp = Blueprint("student_bp", __name__)

def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"


# Get all students (Admin only)
@student_bp.route("/students", methods=["GET"])
@jwt_required()
def get_all_students():
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    students = []
    for student in users_collection.find({"role": "student"}):
        student["_id"] = str(student["_id"])
        students.append(student)

    return jsonify(students), 200


# Assign courses to a student (Admin only)
@student_bp.route("/students/<student_id>/assign-courses", methods=["PUT"])
@jwt_required()
def assign_courses(student_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    data = request.json
    course_ids = data.get("course_ids", [])

    # Validate student exists
    student = users_collection.find_one({"_id": ObjectId(student_id), "role": "student"})
    if not student:
        return jsonify({"error": "Student not found"}), 404

    # Validate all course IDs exist
    valid_course_ids = []
    for course_id in course_ids:
        course = courses_collection.find_one({"_id": ObjectId(course_id)})
        if course:
            valid_course_ids.append(course_id)

    # Update student document with assigned courses
    users_collection.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": {"courses": valid_course_ids}}
    )

    return jsonify({"message": "Courses assigned successfully!"}), 200