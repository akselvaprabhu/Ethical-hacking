from app import create_app
from database import db
from models.user import User
from models.api_log import ApiLog
from models.security_event import SecurityEvent
from models.blocked_ip import BlockedIp
from models.alert import Alert

def reset_all_data():
    app = create_app()
    with app.app_context():
        # Clear all traffic logs, security events, blocked IPs, and alerts
        num_logs = ApiLog.query.delete()
        num_events = SecurityEvent.query.delete()
        num_blocked = BlockedIp.query.delete()
        num_alerts = Alert.query.delete()
        
        # Ensure default admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)

        # Ensure default standard user exists
        demo_user = User.query.filter_by(username='user').first()
        if not demo_user:
            demo_user = User(username='user', role='user')
            demo_user.set_password('user123')
            db.session.add(demo_user)

        db.session.commit()
        print(f"DATABASE RESET COMPLETE: Cleared {num_logs} logs, {num_events} security events, {num_blocked} blocked IPs, and {num_alerts} alerts.")

if __name__ == '__main__':
    reset_all_data()
