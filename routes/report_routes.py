from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.feedback_model import feedback_collection
import io, csv, datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

report_bp = Blueprint("report_bp", __name__)

# -------------------------------
# Export as CSV
# -------------------------------
@report_bp.route("/export/csv", methods=["GET"])
@jwt_required()
def export_csv():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Access denied. Only admin can export reports."}), 403

    feedbacks = list(feedback_collection.find({}, {"_id": 0}))
    if not feedbacks:
        return jsonify({"error": "No feedback data found"}), 404

    # Create CSV in memory
    output = io.StringIO()
    fieldnames = ["student_id", "course_id", "semester", "course_name", "instructor", "rating", "comment", "timestamp"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(feedbacks)

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=feedback_report_{timestamp}.csv"
    return response


# -------------------------------
# Export as PDF
# -------------------------------
@report_bp.route("/export/pdf", methods=["GET"])
@jwt_required()
def export_pdf():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Access denied. Only admin can export reports."}), 403

    feedbacks = list(feedback_collection.find({}, {"_id": 0}))
    if not feedbacks:
        return jsonify({"error": "No feedback data found"}), 404

    # Prepare PDF table data
    headers = ["Student ID", "Course", "Instructor", "Semester", "Rating", "Comment", "Timestamp"]
    data = [headers]
    for fb in feedbacks:
        data.append([
            fb.get("student_id", ""),
            fb.get("course_name", ""),
            fb.get("instructor", ""),
            fb.get("semester", ""),
            str(fb.get("rating", "")),
            fb.get("comment", ""),
            fb.get("timestamp", "").strftime("%Y-%m-%d %H:%M") if isinstance(fb.get("timestamp"), datetime.datetime) else str(fb.get("timestamp"))
        ])

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    title = Paragraph("Student Feedback Report", styles["Heading1"])
    subtitle = Paragraph(f"Generated on {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    doc.build([title, subtitle, Spacer(1, 12), table])
    buffer.seek(0)

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=feedback_report_{timestamp}.pdf"}
    )
