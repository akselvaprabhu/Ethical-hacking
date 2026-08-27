from datetime import datetime, timedelta
from database import db
from models.api_log import ApiLog

def get_recent_request_stats(ip_address, window_seconds=60):
    """
    Retrieves request stats for an IP address in the past window_seconds:
    - total_requests: count
    - failed_logins: count of 401 status on /api/login
    - status_4xx_count: count
    - status_5xx_count: count
    """
    cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
    logs = ApiLog.query.filter(ApiLog.ip_address == ip_address, ApiLog.timestamp >= cutoff).all()

    total_requests = len(logs)
    failed_logins = sum(1 for l in logs if l.endpoint == '/api/login' and l.status_code == 401)
    status_4xx = sum(1 for l in logs if 400 <= l.status_code < 500)
    status_5xx = sum(1 for l in logs if 500 <= l.status_code < 600)
    auth_failures = sum(1 for l in logs if l.status_code == 401)

    return {
        'total_requests': total_requests,
        'failed_logins': failed_logins,
        'status_4xx_count': status_4xx,
        'status_5xx_count': status_5xx,
        'auth_failures': auth_failures
    }
