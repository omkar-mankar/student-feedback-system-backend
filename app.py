from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Import blueprints
from routes.auth_routes import auth_bp
from routes.course_routes import course_bp
from routes.student_routes import student_bp

from routes.report_routes import report_bp 

from routes.feedback_routes import feedback_bp



app = Flask(__name__)
CORS(app)               # Allow cross-origin requests (Frontend ↔ Backend)

# JWT Config
app.config["JWT_SECRET_KEY"] = "supersecretkey"  # Change in production
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(course_bp)
app.register_blueprint(student_bp)
app.register_blueprint(report_bp)
app.register_blueprint(feedback_bp)


if __name__ == "__main__":
    app.run(debug=True)            # Start Flask server in debug mode