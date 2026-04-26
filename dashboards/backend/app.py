from flask import Flask, jsonify
from flask_cors import CORS
from dashboards.backend.api_v1 import api_bp
from core.config_manager import get_config

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    config = get_config()
    app.config.from_mapping(
        SECRET_KEY="darkwin_secret_key_change_me",
        SQLALCHEMY_DATABASE_URI=config.database.url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Register Blueprints
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    
    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "platform": "DARKWIN"})
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
