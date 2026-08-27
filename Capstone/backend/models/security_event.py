from datetime import datetime
from database import db

class SecurityEvent(db.Model):
    __tablename__ = 'security_events'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)
    endpoint = db.Column(db.String(255), nullable=False)
    attack_type = db.Column(db.String(50), nullable=False) # e.g. Brute Force, Injection, Anomaly, Rate Limit
    risk_score = db.Column(db.Integer, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    detection_method = db.Column(db.String(30), nullable=False) # SIGNATURE, ML, HYBRID
    reason = db.Column(db.Text, nullable=False)
    action_taken = db.Column(db.String(30), nullable=False) # ALLOW, MONITOR, RATE_LIMIT, BLOCK

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': self.ip_address,
            'endpoint': self.endpoint,
            'attack_type': self.attack_type,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'detection_method': self.detection_method,
            'reason': self.reason,
            'action_taken': self.action_taken
        }
