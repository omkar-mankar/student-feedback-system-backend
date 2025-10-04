from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.course_model import courses_collection
from bson import ObjectId

course_bp = Blueprint("course_bp", __name__)

def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"

# Add Course / Subject (Admin only)
@course_bp.route("/courses", methods=["POST"])
@jwt_required()
def add_course():
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    data = request.json
    if not data.get("course_name") or not data.get("semester"):
        return jsonify({"error": "course_name and semester are required"}), 400

    if courses_collection.find_one({"course_name": data["course_name"], "semester": data["semester"]}):
        return jsonify({"error": "Course already exists in this semester"}), 400

    course = {
        "course_name": data["course_name"],
        "instructor": data.get("instructor", ""),
        "semester": data["semester"],
        "description": data.get("description", "")
    }
    courses_collection.insert_one(course)
    return jsonify({"message": "Course added successfully!"}), 201

# Get all courses
@course_bp.route("/courses", methods=["GET"])
@jwt_required()
def get_courses():
    courses = []
    for course in courses_collection.find():
        course["_id"] = str(course["_id"])
        courses.append(course)
    return jsonify(courses), 200

# Get courses by semester
@course_bp.route("/courses/semester/<semester>", methods=["GET"])
@jwt_required()
def get_courses_by_semester(semester):
    courses = []
    for course in courses_collection.find({"semester": semester}):
        course["_id"] = str(course["_id"])
        courses.append(course)
    return jsonify(courses), 200

# Get course details
@course_bp.route("/courses/<course_id>", methods=["GET"])
@jwt_required()
def get_single_course(course_id):
    course = courses_collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        return jsonify({"error": "Course not found"}), 404
    course["_id"] = str(course["_id"])
    return jsonify(course), 200

# Update course
@course_bp.route("/courses/<course_id>", methods=["PATCH"])
@jwt_required()
def patch_course(course_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    data = request.json
    update_data = {}
    for field in ["course_name", "instructor", "semester", "description"]:
        if field in data:
            update_data[field] = data[field]

    result = courses_collection.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Course not found"}), 404
    return jsonify({"message": "Course updated successfully!"}), 200


# Delete course
@course_bp.route("/courses/<course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403
    result = courses_collection.delete_one({"_id": ObjectId(course_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Course not found"}), 404
    return jsonify({"message": "Course deleted successfully!"}), 200