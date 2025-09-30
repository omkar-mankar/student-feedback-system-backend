from flask import Blueprint, request, jsonify
from models.feedback_model import feedback_collection
from models.course_model import courses_collection
from models.user_model import admins_collection, students_collection
from bson import ObjectId
import datetime

feedback_bp = Blueprint("feedback_bp", __name__)

def get_current_user(request):
    user_id = request.cookies.get("user_id")
    role = request.cookies.get("role")
    if not user_id or not role:
        return None
    collection = admins_collection if role == "admin" else students_collection
    return collection.find_one({"_id": ObjectId(user_id)})

# Submit feedback
@feedback_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return jsonify({"error": "Student login required"}), 403

    data = request.json
    if not data.get("course_id") or not data.get("rating"):
        return jsonify({"error": "course_id and rating are required"}), 400

    course = courses_collection.find_one({"_id": ObjectId(data["course_id"])})
    if not course:
        return jsonify({"error": "Invalid course"}), 400

    feedback = {
        "student_id": str(user["_id"]),
        "course_id": data["course_id"],
        "semester": course["semester"],
        "course_name": course["course_name"],
        "instructor": course["instructor"],
        "rating": data["rating"],
        "comment": data.get("comment", ""),
        "timestamp": datetime.datetime.utcnow()
    }
    feedback_collection.insert_one(feedback)
    return jsonify({"message": "Feedback submitted successfully"}), 201

# Get all feedback (admin only)
@feedback_bp.route("/feedback/all", methods=["GET"])
def get_all_feedback():
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    feedbacks = []
    for fb in feedback_collection.find():
        fb["_id"] = str(fb["_id"])
        feedbacks.append(fb)
    return jsonify(feedbacks), 200



# from flask import Blueprint, request, jsonify
# from models.feedback_model import feedback_collection   # Feedback collection
# from models.user_model import students_collection, admins_collection
# from bson import ObjectId
# import datetime

# feedback_bp = Blueprint("feedback_bp", __name__)

# # ---------------------------
# # Helper: Get current user from cookies
# # ---------------------------
# def get_current_user(request):
#     user_id = request.cookies.get("user_id")
#     role = request.cookies.get("role")

#     if not user_id or not role:
#         return None

#     collection = admins_collection if role == "admin" else students_collection
#     user = collection.find_one({"_id": ObjectId(user_id)})
#     return user


# # ---------------------------
# # Submit Feedback (Student only)
# # ---------------------------
# @feedback_bp.route("/feedback", methods=["POST"])
# def submit_feedback():
#     user = get_current_user(request)
#     if not user or user["role"] != "student":
#         return jsonify({"error": "Student login required"}), 403

#     data = request.json
#     if not data.get("course_id") or not data.get("rating"):
#         return jsonify({"error": "course_id and rating are required"}), 400

#     feedback = {
#         "student_id": str(user["_id"]),
#         "course_id": data["course_id"],
#         "rating": data["rating"],
#         "comment": data.get("comment", ""),
#         "timestamp": datetime.datetime.utcnow()
#     }
#     feedback_collection.insert_one(feedback)
#     return jsonify({"message": "Feedback submitted successfully"}), 201


# # ---------------------------
# # Get All Feedback (Admin only)
# # ---------------------------
# @feedback_bp.route("/feedback", methods=["GET"])
# def get_all_feedback():
#     user = get_current_user(request)
#     if not user or user["role"] != "admin":
#         return jsonify({"error": "Admin access required"}), 403

#     feedbacks = []
#     for fb in feedback_collection.find():
#         fb["_id"] = str(fb["_id"])
#         feedbacks.append(fb)

#     return jsonify(feedbacks), 200


# # ---------------------------
# # Delete Feedback (Admin only)
# # ---------------------------
# @feedback_bp.route("/feedback/<feedback_id>", methods=["DELETE"])
# def delete_feedback(feedback_id):
#     user = get_current_user(request)
#     if not user or user["role"] != "admin":
#         return jsonify({"error": "Admin access required"}), 403

#     result = feedback_collection.delete_one({"_id": ObjectId(feedback_id)})
#     if result.deleted_count == 0:
#         return jsonify({"error": "Feedback not found"}), 404

#     return jsonify({"message": "Feedback deleted successfully"}), 200


