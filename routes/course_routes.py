from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.course_model import courses_collection
from bson import ObjectId

course_bp = Blueprint("course_bp", __name__)

def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"


# Add Course (Admin only) with duplicate validation
@course_bp.route("/courses", methods=["POST"])
@jwt_required()
def add_course():
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    data = request.json
    if not data.get("course_name"):
        return jsonify({"error": "course_name is required"}), 400

    # Check for duplicate course name
    if courses_collection.find_one({"course_name": data["course_name"]}):
        return jsonify({"error": "Course with this name already exists"}), 400

    course = {
        "course_name": data["course_name"],
        "instructor": data.get("instructor", "")
    }
    courses_collection.insert_one(course)
    return jsonify({"message": "Course added successfully!"}), 201


# Get All Courses (Both Admin & Students)
@course_bp.route("/courses", methods=["GET"])
@jwt_required()
def get_courses():
    courses = []
    for course in courses_collection.find():
        course["_id"] = str(course["_id"])
        courses.append(course)
    return jsonify(courses), 200


# Get Single Course by ID (Both Admin & Students)
@course_bp.route("/courses/<course_id>", methods=["GET"])
@jwt_required()
def get_single_course(course_id):
    course = courses_collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        return jsonify({"error": "Course not found"}), 404

    course["_id"] = str(course["_id"])
    return jsonify(course), 200


# Update Course (Admin only)
@course_bp.route("/courses/<course_id>", methods=["PUT"])
@jwt_required()
def update_course(course_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    data = request.json
    result = courses_collection.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": {"course_name": data.get("course_name"), "instructor": data.get("instructor", "")}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "Course not found"}), 404

    return jsonify({"message": "Course updated successfully!"}), 200


# Delete Course (Admin only)
@course_bp.route("/courses/<course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    result = courses_collection.delete_one({"_id": ObjectId(course_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Course not found"}), 404

    return jsonify({"message": "Course deleted successfully!"}), 200