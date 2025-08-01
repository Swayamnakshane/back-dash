from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError
from mongoengine import connect

from .config import Config
from .routes.admin_route import admin_bp
from .routes.employe_route import employee_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Initialize MongoDB
    connect(host=app.config['MONGODB_SETTINGS']['host'])

    # ✅ CORS and JWT
    CORS(app, supports_credentials=True, origins="*")
    jwt = JWTManager(app)

    # ✅ Register Blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(employee_bp, url_prefix='/employee')

    # ✅ JWT Error Handlers
    @app.errorhandler(NoAuthorizationError)
    def handle_missing_token(e):
        return jsonify({'error': 'Token is missing or expired.'}), 401

    @app.errorhandler(JWTDecodeError)
    def handle_invalid_token(e):
        return jsonify({'error': 'Invalid token format.'}), 401

    return app
