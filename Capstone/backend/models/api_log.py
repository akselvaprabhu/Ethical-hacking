from datetime import datetime
from database import db

class ApiLog(db.Model):
    __tablename__ = 'api_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)
    method = db.Column(db.String(10), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    response_time_ms = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    risk_score = db.Column(db.Integer, default=0)
    action_taken = db.Column(db.String(30), default='ALLOW') # ALLOW, RATE_LIMIT, BLOCK
    
    user = db.relationship('User', backref=db.backref('api_logs', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': self.ip_address,
            'method': self.method,
            'endpoint': self.endpoint,
            'status_code': self.status_code,
            'response_time_ms': round(self.response_time_ms, 2),
            'user_id': self.user_id,
            'risk_score': self.risk_score,
            'action_taken': self.action_taken
        }
