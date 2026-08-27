import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import db, init_db
from routes import auth_bp, api_bp, security_bp
from middleware.traffic_monitor import setup_traffic_monitor
from ml.detector import get_model_payload

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable Cross-Origin Resource Sharing (CORS) for dashboard integration
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Initialize SQLAlchemy database
    init_db(app)

    # Pre-load/train ML Anomaly Detection model
    with app.app_context():
        try:
            get_model_payload()
            print("ML Model loaded successfully.")
        except Exception as e:
            print(f"Warning: ML model initialization delayed: {e}")

    # Setup automatic Traffic Monitor & Runtime Protection middleware
    setup_traffic_monitor(app)

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(security_bp)

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ONLINE',
            'framework': 'Intelligent API Attack Detection & Runtime Protection',
            'timestamp': os.getenv('CURRENT_TIME', '2026-08-23')
        }), 200

    return app

app = create_app()

if __name__ == '__main__':
    # Auto-seed database if running directly
    from seed_data import seed_database
    with app.app_context():
        seed_database()
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Intelligent API Security Framework backend on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
