from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.feedback_model import feedback_collection
import io, csv
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

report_bp = Blueprint("report_bp", __name__)

# ---------------------------
# Export as CSV
# ---------------------------
@report_bp.route("/export/csv", methods=["GET"])
@jwt_required()
def export_csv():
    claims = get_jwt()  # get role info from JWT claims
    if claims.get("role") != "admin":
        return jsonify({"error": "Access denied. Only admin can export reports."}), 403

    feedbacks = list(feedback_collection.find({}, {"_id": 0}))
    if not feedbacks:
        return jsonify({"error": "No feedback data found"}), 404

    # Create CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=feedbacks[0].keys())
    writer.writeheader()
    writer.writerows(feedbacks)

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=feedback_report.csv"
    return response


# ---------------------------
# Export as PDF
# ---------------------------
@report_bp.route("/export/pdf", methods=["GET"])
@jwt_required()
def export_pdf():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Access denied. Only admin can export reports."}), 403

    feedbacks = list(feedback_collection.find({}, {"_id": 0}))
    if not feedbacks:
        return jsonify({"error": "No feedback data found"}), 404

    # Prepare table data
    data = [list(feedbacks[0].keys())]  # headers
    for fb in feedbacks:
        data.append(list(fb.values()))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    doc.build([table])
    buffer.seek(0)

    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=feedback_report.pdf"}
    )
