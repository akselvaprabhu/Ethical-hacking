from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from database import db
from models.api_log import ApiLog
from models.security_event import SecurityEvent
from models.blocked_ip import BlockedIp
from models.alert import Alert
from protection.firewall import unblock_ip_address, block_ip_address

security_bp = Blueprint('security', __name__)

@security_bp.route('/api/security/stats', methods=['GET'])
def get_security_stats():
    total_requests = ApiLog.query.count()
    normal_requests = ApiLog.query.filter_by(action_taken='ALLOW').count()
    suspicious_requests = ApiLog.query.filter(ApiLog.action_taken.in_(['MONITOR', 'RATE_LIMIT'])).count()
    blocked_requests = ApiLog.query.filter_by(action_taken='BLOCKED').count()
    active_blocked_ips = BlockedIp.query.filter_by(is_active=True).count()

    # Attack distribution counts
    brute_force_count = SecurityEvent.query.filter(SecurityEvent.attack_type.like('%Brute Force%')).count()
    anomaly_count = SecurityEvent.query.filter(SecurityEvent.attack_type.like('%Anomaly%')).count()
    sqli_count = SecurityEvent.query.filter(SecurityEvent.attack_type.like('%SQL Injection%')).count()
    xss_count = SecurityEvent.query.filter(SecurityEvent.attack_type.like('%Scripting%')).count()
    rate_limit_count = SecurityEvent.query.filter(SecurityEvent.attack_type.like('%Rate Limit%')).count()

    return jsonify({
        'success': True,
        'overview': {
            'total_requests': total_requests,
            'normal_requests': normal_requests,
            'suspicious_requests': suspicious_requests,
            'blocked_requests': blocked_requests,
            'active_threats': active_blocked_ips
        },
        'attack_distribution': [
            {'name': 'Brute Force', 'count': brute_force_count},
            {'name': 'ML Anomaly', 'count': anomaly_count},
            {'name': 'SQL Injection', 'count': sqli_count},
            {'name': 'Cross-Site Scripting', 'count': xss_count},
            {'name': 'Rate Limit Violation', 'count': rate_limit_count}
        ]
    }), 200

@security_bp.route('/api/security/traffic-chart', methods=['GET'])
def get_traffic_chart():
    # Group logs by hour or recent minutes
    now = datetime.now()
    chart_data = []


    for i in range(12, -1, -1):
        time_slot = now - timedelta(minutes=i * 5)
        slot_start = time_slot - timedelta(minutes=5)
        slot_label = time_slot.strftime('%H:%M')

        total = ApiLog.query.filter(ApiLog.timestamp >= slot_start, ApiLog.timestamp <= time_slot).count()
        blocked = ApiLog.query.filter(ApiLog.timestamp >= slot_start, ApiLog.timestamp <= time_slot, ApiLog.action_taken == 'BLOCKED').count()
        suspicious = ApiLog.query.filter(ApiLog.timestamp >= slot_start, ApiLog.timestamp <= time_slot, ApiLog.action_taken != 'ALLOW').count()

        chart_data.append({
            'time': slot_label,
            'total': total,
            'suspicious': suspicious,
            'blocked': blocked
        })

    return jsonify({'success': True, 'chart_data': chart_data}), 200

@security_bp.route('/api/security/logs', methods=['GET'])
def get_security_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    logs_query = ApiLog.query.order_by(ApiLog.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'logs': [log.to_dict() for log in logs_query.items],
        'total': logs_query.total,
        'pages': logs_query.pages,
        'current_page': page
    }), 200

@security_bp.route('/api/security/events', methods=['GET'])
def get_security_events():
    events = SecurityEvent.query.order_by(SecurityEvent.timestamp.desc()).limit(50).all()
    return jsonify({
        'success': True,
        'count': len(events),
        'events': [e.to_dict() for e in events]
    }), 200

@security_bp.route('/api/security/blocked-ips', methods=['GET'])
def get_blocked_ips():
    blocked = BlockedIp.query.order_by(BlockedIp.blocked_at.desc()).all()
    return jsonify({
        'success': True,
        'blocked_ips': [b.to_dict() for b in blocked]
    }), 200

@security_bp.route('/api/security/unblock-ip', methods=['POST'])
def unblock_ip():
    data = request.get_json() or {}
    ip_address = data.get('ip_address')

    if not ip_address:
        return jsonify({'success': False, 'message': 'IP address required'}), 400

    result = unblock_ip_address(ip_address)
    if result:
        return jsonify({'success': True, 'message': f'IP address {ip_address} has been unblocked.'}), 200
    else:
        return jsonify({'success': False, 'message': f'IP address {ip_address} was not found in active blocks.'}), 444

@security_bp.route('/api/security/block-ip', methods=['POST'])
def manual_block_ip():
    data = request.get_json() or {}
    ip_address = data.get('ip_address')
    reason = data.get('reason', 'Manual Administrator Block')
    duration = data.get('duration_minutes', 30)

    if not ip_address:
        return jsonify({'success': False, 'message': 'IP address required'}), 400

    block_ip_address(ip_address, reason=reason, duration_minutes=duration)
    return jsonify({'success': True, 'message': f'IP address {ip_address} manually blocked for {duration}m.'}), 200

@security_bp.route('/api/security/reset', methods=['POST'])
def reset_security_data():
    ApiLog.query.delete()
    SecurityEvent.query.delete()
    BlockedIp.query.delete()
    Alert.query.delete()
    db.session.commit()
    return jsonify({'success': True, 'message': 'All security logs, events, threats, and blocked IPs reset to ZERO.'}), 200

@security_bp.route('/api/security/alerts', methods=['GET'])
def get_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(20).all()
    return jsonify({
        'success': True,
        'alerts': [a.to_dict() for a in alerts]
    }), 200

