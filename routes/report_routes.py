""" from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.feedback_model import feedback_collection   # MongoDB collection for feedback
import io, csv
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# Create a new blueprint for report export APIs
report_bp = Blueprint("report_bp", __name__)

# -- CSV Export --
@report_bp.route("/export/csv", methods=["GET"])
@jwt_required()  # Require JWT authentication
def export_csv():
    user = get_jwt_identity()  # Get the logged-in user from the token
    if user["role"] != "admin":  # Only Admin is allowed
        return jsonify({"error": "Access denied. Only admin can export reports."}), 403

    # Fetch all feedback data from MongoDB (ignoring _id field)
    feedbacks = list(feedback_collection.find({}, {"_id": 0}))
    if not feedbacks:
        return jsonify({"error": "No feedback data found"}), 404

    # Create an in-memory CSV file
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=feedbacks[0].keys())  # CSV headers = keys
    writer.writeheader()
    writer.writerows(feedbacks)  # Write feedback rows

    # Send file as response
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=feedback_report.csv"
    return response


# --- PDF Export ---
@report_bp.route("/export/pdf", methods=["GET"])
@jwt_required()  # Require JWT authentication
def export_pdf():
    user = get_jwt_identity()  # Get the logged-in user from the token
    if user["role"] != "admin":  # Only Admin is allowed
        return jsonify({"error": "Access denied. Only admin can export reports."}), 403

    # Fetch all feedback data from MongoDB (ignoring _id field)
    feedbacks = list(feedback_collection.find({}, {"_id": 0}))
    if not feedbacks:
        return jsonify({"error": "No feedback data found"}), 404

    # Convert feedback data into table format for PDF
    data = [list(feedbacks[0].keys())]  # First row = column headers
    for fb in feedbacks:
        data.append(list(fb.values()))  # Add each feedback as row

    # Create in-memory PDF file
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    # Build table for PDF
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),        # Header background color
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),   # Header text color
        ("ALIGN", (0,0), (-1,-1), "CENTER"),               # Center align text
        ("GRID", (0,0), (-1,-1), 1, colors.black),         # Add grid lines
    ]))
    doc.build([table])  # Generate PDF with the table

    # Send PDF file as response
    buffer.seek(0)
    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=feedback_report.pdf"}
    )
  """