from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Import blueprints
from routes.auth_routes import auth_bp

app = Flask(__name__)
CORS(app)

# JWT Config
app.config["JWT_SECRET_KEY"] = "supersecretkey"  # Change this in production
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)