# routes\feedback_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.feedback_model import feedback_collection
from models.course_model import courses_collection
from models.user_model import students_collection
from bson import ObjectId
import datetime

# Utility function to check if the user is an admin
def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"

feedback_bp = Blueprint("feedback_bp", __name__)

# Submit or edit feedback
@feedback_bp.route("/feedback", methods=["POST"])
@jwt_required()
def submit_feedback():
    student_id = get_jwt_identity()
    student = students_collection.find_one({"_id": ObjectId(student_id)})

    if not student or student.get("role") != "student":
        return jsonify({"error": "Student login required"}), 403

    data = request.json
    if not data.get("course_id") or not data.get("rating"):
        return jsonify({"error": "course_id and rating required"}), 400

    course = courses_collection.find_one({"_id": ObjectId(data["course_id"])})
    if not course:
        return jsonify({"error": "Invalid course"}), 400

    # Check if feedback already exists
    existing_feedback = feedback_collection.find_one({
        "student_id": str(student["_id"]),
        "course_id": data["course_id"]
    })

    feedback_data = {
        "student_id": str(student["_id"]),
        "course_id": data["course_id"],
        "semester": course["semester"],
        "course_name": course["course_name"],
        "instructor": course["instructor"],
        "rating": data["rating"],
        "comment": data.get("comment", ""),
        "timestamp": datetime.datetime.utcnow()
    }

    if existing_feedback:
        # Update existing feedback
        feedback_collection.update_one(
            {"_id": existing_feedback["_id"]},
            {"$set": feedback_data}
        )
        return jsonify({"message": "Feedback updated successfully!"}), 200
    else:
        # Insert new feedback
        feedback_collection.insert_one(feedback_data)
        return jsonify({"message": "Feedback submitted successfully!"}), 201


# Get my feedbacks
@feedback_bp.route("/feedback/my", methods=["GET"])
@jwt_required()
def get_my_feedbacks():
    student_id = get_jwt_identity()
    student = students_collection.find_one({"_id": ObjectId(student_id)})

    if not student or student.get("role") != "student":
        return jsonify({"error": "Student login required"}), 403

    feedbacks = list(feedback_collection.find({"student_id": str(student["_id"])}))
    for fb in feedbacks:
        fb["_id"] = str(fb["_id"])
    return jsonify(feedbacks), 200

# Delete feedback
@feedback_bp.route("/feedback/<feedback_id>", methods=["DELETE"])
@jwt_required()
def delete_feedback(feedback_id):
    student_id = get_jwt_identity()
    student = students_collection.find_one({"_id": ObjectId(student_id)})

    if not student or student.get("role") != "student":
        return jsonify({"error": "Student login required"}), 403

    result = feedback_collection.delete_one({
        "_id": ObjectId(feedback_id),
        "student_id": str(student["_id"])
    })

    if result.deleted_count == 0:
        return jsonify({"error": "Feedback not found"}), 404

    return jsonify({"message": "Feedback deleted successfully!"}), 200


# Admin: Get all feedbacks
@feedback_bp.route("/feedback/all", methods=["GET"])
@jwt_required()
def get_all_feedback():
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    feedbacks = []
    for fb in feedback_collection.find():
        fb["_id"] = str(fb["_id"])
        # add student username
        student = students_collection.find_one({"_id": ObjectId(fb["student_id"])})
        fb["student_name"] = student["username"] if student else "Unknown"
        # add course name
        course = courses_collection.find_one({"_id": ObjectId(fb["course_id"])})
        fb["course_name"] = course["course_name"] if course else "Unknown"
        feedbacks.append(fb)
    return jsonify(feedbacks), 200

    # Get feedback for logged-in student
@feedback_bp.route("/feedback/student", methods=["GET"])
@jwt_required()
def get_my_feedback():
    student_id = get_jwt_identity()  # student _id
    feedbacks = list(feedback_collection.find({"student_id": student_id}))
    for fb in feedbacks:
        fb["_id"] = str(fb["_id"])
        course = courses_collection.find_one({"_id": ObjectId(fb["course_id"])})
        fb["course_name"] = course["course_name"] if course else "Unknown"
    return jsonify(feedbacks)