from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from auth.routes import auth_bp

# Import models
from auth.models import db  # Import the initialized db instance from auth
from auth.models import User, TokenBlocklist, ResetToken

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    mail.init_app(app)
    CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5173"}},
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Authorization", "Content-Type", "X-Requested-With"])

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({"msg": "Missing or invalid token"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"msg": "Invalid token"}), 422

    with app.app_context():
        db.create_all()  # Ensure all models are registered

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
