import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_cyber_security_secret_2026')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "api_security.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_EXPIRATION_HOURS = 24
    
    # Dynamic Protection Configuration
    BLOCK_DURATION_MINUTES = int(os.getenv('BLOCK_DURATION_MINUTES', 15))
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 20))
    MAX_FAILED_LOGINS = int(os.getenv('MAX_FAILED_LOGINS', 5))
    RISK_BLOCK_THRESHOLD = int(os.getenv('RISK_BLOCK_THRESHOLD', 65))
    ML_ANOMALY_THRESHOLD = float(os.getenv('ML_ANOMALY_THRESHOLD', -0.15))
