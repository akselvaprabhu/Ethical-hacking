from datetime import datetime, timedelta
from database import db
from models.user import User
from models.api_log import ApiLog
from models.security_event import SecurityEvent
from models.blocked_ip import BlockedIp
from models.alert import Alert

def seed_database():
    db.create_all()

    # Seed Admin User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    # Seed Standard Demo User
    demo_user = User.query.filter_by(username='user').first()
    if not demo_user:
        demo_user = User(username='user', role='user')
        demo_user.set_password('user123')
        db.session.add(demo_user)

    db.session.commit()

    # Seed initial API logs if database is empty
    if ApiLog.query.count() == 0:
        now = datetime.utcnow()
        sample_logs = [
            ApiLog(timestamp=now - timedelta(minutes=45), ip_address='192.168.1.10', method='POST', endpoint='/api/login', status_code=200, response_time_ms=45.2, risk_score=5, action_taken='ALLOW'),
            ApiLog(timestamp=now - timedelta(minutes=42), ip_address='192.168.1.10', method='GET', endpoint='/api/products', status_code=200, response_time_ms=12.4, risk_score=5, action_taken='ALLOW'),
            ApiLog(timestamp=now - timedelta(minutes=35), ip_address='192.168.1.10', method='GET', endpoint='/api/orders', status_code=200, response_time_ms=28.1, risk_score=10, action_taken='ALLOW'),
            
            # Suspicious Brute Force attempt log
            ApiLog(timestamp=now - timedelta(minutes=25), ip_address='203.0.113.45', method='POST', endpoint='/api/login', status_code=401, response_time_ms=18.5, risk_score=45, action_taken='MONITOR'),
            ApiLog(timestamp=now - timedelta(minutes=24), ip_address='203.0.113.45', method='POST', endpoint='/api/login', status_code=401, response_time_ms=15.0, risk_score=65, action_taken='MONITOR'),
            ApiLog(timestamp=now - timedelta(minutes=23), ip_address='203.0.113.45', method='POST', endpoint='/api/login', status_code=403, response_time_ms=8.0, risk_score=85, action_taken='BLOCKED'),
            
            # Injection attempt log
            ApiLog(timestamp=now - timedelta(minutes=15), ip_address='198.51.100.88', method='GET', endpoint='/api/products?search=\' OR \'1\'=\'1', status_code=403, response_time_ms=10.2, risk_score=90, action_taken='BLOCKED'),

            # Normal API calls
            ApiLog(timestamp=now - timedelta(minutes=10), ip_address='127.0.0.1', method='GET', endpoint='/api/products', status_code=200, response_time_ms=14.0, risk_score=0, action_taken='ALLOW'),
            ApiLog(timestamp=now - timedelta(minutes=5), ip_address='127.0.0.1', method='GET', endpoint='/api/profile', status_code=200, response_time_ms=19.3, risk_score=5, action_taken='ALLOW')
        ]
        db.session.add_all(sample_logs)

    # Seed initial Security Events
    if SecurityEvent.query.count() == 0:
        now = datetime.utcnow()
        sample_events = [
            SecurityEvent(
                timestamp=now - timedelta(minutes=23),
                ip_address='203.0.113.45',
                endpoint='/api/login',
                attack_type='Brute Force Attack',
                risk_score=85,
                risk_level='CRITICAL',
                detection_method='SIGNATURE',
                reason='Multiple failed login attempts from same IP address within 60s',
                action_taken='BLOCKED'
            ),
            SecurityEvent(
                timestamp=now - timedelta(minutes=15),
                ip_address='198.51.100.88',
                endpoint='/api/products',
                attack_type='SQL Injection',
                risk_score=90,
                risk_level='CRITICAL',
                detection_method='HYBRID',
                reason='SQL Injection signature pattern detected in query parameter: OR 1=1',
                action_taken='BLOCKED'
            )
        ]
        db.session.add_all(sample_events)

    # Seed initial Blocked IPs
    if BlockedIp.query.count() == 0:
        now = datetime.utcnow()
        sample_blocked = [
            BlockedIp(
                ip_address='203.0.113.45',
                reason='Brute Force Attack: Repeated failed logins',
                blocked_at=now - timedelta(minutes=23),
                expires_at=now + timedelta(minutes=37),
                is_active=True
            ),
            BlockedIp(
                ip_address='198.51.100.88',
                reason='SQL Injection Attack attempt',
                blocked_at=now - timedelta(minutes=15),
                expires_at=now + timedelta(minutes=45),
                is_active=True
            )
        ]
        db.session.add_all(sample_blocked)

    # Seed initial Alerts
    if Alert.query.count() == 0:
        now = datetime.utcnow()
        sample_alerts = [
            Alert(
                timestamp=now - timedelta(minutes=23),
                severity='CRITICAL',
                title='IP Blocked: 203.0.113.45',
                message='IP 203.0.113.45 automatically blocked for 60m due to Brute Force login attempts.',
                is_read=False
            ),
            Alert(
                timestamp=now - timedelta(minutes=15),
                severity='CRITICAL',
                title='SQL Injection Detected',
                message='High risk payload blocked from IP 198.51.100.88 targeting endpoint /api/products.',
                is_read=False
            )
        ]
        db.session.add_all(sample_alerts)

    db.session.commit()
    print("Database seeded with default admin credentials & sample cybersecurity data.")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database()
