import time
from datetime import datetime
from flask import request, jsonify, g
from database import db
from models.api_log import ApiLog
from models.security_event import SecurityEvent
from protection.firewall import check_ip_blocked, block_ip_address
from protection.rate_limiter import get_recent_request_stats
from detection.signature_engine import analyze_signature
from ml.detector import predict_anomaly
from utils.risk_scorer import calculate_risk_score

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'

def setup_traffic_monitor(app):

    @app.before_request
    def monitor_and_protect_request():
        # Store start time for latency tracking
        g.start_time = time.time()
        client_ip = get_client_ip()
        g.client_ip = client_ip
        endpoint = request.path

        # 0. Allow OPTIONS preflight requests for CORS
        if request.method == 'OPTIONS':
            return None

        # Exclude static files and security telemetry endpoints from pre-flight IP blocking
        if endpoint.startswith('/static') or endpoint.startswith('/api/security'):
            g.security_context = {'risk_score': 0, 'action': 'ALLOW'}
            return None




        # 1. Pre-flight Firewall Check (Blocked IP filter)
        is_blocked, block_info = check_ip_blocked(client_ip)
        if is_blocked:
            # Analyze payload even on blocked IPs so signature attacks (SQLi, XSS) are logged in SecurityEvents & charts!
            stats = get_recent_request_stats(client_ip, window_seconds=60)
            sig_results = analyze_signature(request, recent_failed_logins=stats['failed_logins'], recent_ip_requests=stats['total_requests'] + 1)
            
            attack_type = sig_results['attack_types'][0] if sig_results['attack_types'] else 'Blocked IP Access Attempt'
            reason = sig_results['reasons'][0] if sig_results['reasons'] else (block_info.reason if block_info else 'Security Threat')

            # Log blocked request attempt in ApiLog
            log_entry = ApiLog(
                timestamp=datetime.now(),
                ip_address=client_ip,
                method=request.method,
                endpoint=endpoint,
                status_code=403,
                response_time_ms=0.0,
                risk_score=100,
                action_taken='BLOCKED'
            )
            db.session.add(log_entry)

            # Log SecurityEvent for threat charts & incident feed
            sec_event = SecurityEvent(
                timestamp=datetime.now(),
                ip_address=client_ip,
                endpoint=endpoint,
                attack_type=attack_type,
                risk_score=100,
                risk_level='CRITICAL',
                detection_method='SIGNATURE' if sig_results['attack_types'] else 'FIREWALL',
                reason=reason,
                action_taken='BLOCKED'
            )
            db.session.add(sec_event)
            db.session.commit()

            return jsonify({
                'success': False,
                'message': 'Access Denied: Your IP address is blocked.',
                'reason': reason,
                'blocked_until': block_info.expires_at.strftime('%Y-%m-%d %H:%M:%S') if block_info and block_info.expires_at else 'Permanent'
            }), 403


        # 2. Gather traffic statistics from sliding window
        stats = get_recent_request_stats(client_ip, window_seconds=60)
        recent_req_count = stats['total_requests'] + 1 # Include current request
        failed_logins = stats['failed_logins']

        # 3. Signature & Rule-based Detection
        sig_results = analyze_signature(request, recent_failed_logins=failed_logins, recent_ip_requests=recent_req_count)

        # 4. Machine Learning Anomaly Detection
        # Build feature vector
        status_4xx_ratio = (stats['status_4xx_count'] / max(1, stats['total_requests']))
        status_5xx_ratio = (stats['status_5xx_count'] / max(1, stats['total_requests']))
        # Endpoint frequency score (sensitive paths score lower)
        sensitive_paths = ['/api/login', '/api/register', '/admin', '/config']
        freq_score = 0.3 if any(p in endpoint for p in sensitive_paths) else 0.9

        ml_features = {
            'requests_per_min': recent_req_count,
            'failed_logins': failed_logins,
            'endpoint_freq_score': freq_score,
            'status_4xx_ratio': status_4xx_ratio,
            'status_5xx_ratio': status_5xx_ratio,
            'auth_failures': stats['auth_failures']
        }
        ml_prediction = predict_anomaly(ml_features)

        # 5. Risk Scoring Engine
        risk_result = calculate_risk_score(
            signature_results=sig_results,
            ml_anomaly_score=ml_prediction['anomaly_score'],
            failed_login_count=failed_logins,
            request_freq=recent_req_count
        )

        g.security_context = {
            'risk_score': risk_result['risk_score'],
            'risk_level': risk_result['risk_level'],
            'action': risk_result['action'],
            'attack_type': risk_result['attack_type'],
            'reason': risk_result['reason'],
            'detection_method': 'HYBRID' if (sig_results['score'] > 0 and ml_prediction['is_anomaly']) else ('SIGNATURE' if sig_results['score'] > 0 else ('ML' if ml_prediction['is_anomaly'] else 'RULE_ENGINE'))
        }

        # 6. Runtime Protection Action Decision
        if risk_result['action'] == 'BLOCK' or risk_result['risk_score'] >= app.config['RISK_BLOCK_THRESHOLD']:
            # Block the IP address in firewall
            block_reason = risk_result['reason']
            block_ip_address(client_ip, reason=block_reason, duration_minutes=app.config['BLOCK_DURATION_MINUTES'])

            # Log Security Event
            sec_event = SecurityEvent(
                timestamp=datetime.utcnow(),
                ip_address=client_ip,
                endpoint=endpoint,
                attack_type=risk_result['attack_type'],
                risk_score=risk_result['risk_score'],
                risk_level=risk_result['risk_level'],
                detection_method=g.security_context['detection_method'],
                reason=block_reason,
                action_taken='BLOCKED'
            )
            db.session.add(sec_event)

            # Log API traffic entry
            log_entry = ApiLog(
                timestamp=datetime.utcnow(),
                ip_address=client_ip,
                method=request.method,
                endpoint=endpoint,
                status_code=403,
                response_time_ms=round((time.time() - g.start_time) * 1000, 2),
                risk_score=risk_result['risk_score'],
                action_taken='BLOCKED'
            )
            db.session.add(log_entry)
            db.session.commit()

            return jsonify({
                'success': False,
                'message': 'Request blocked by Intelligent Security Framework',
                'attack_type': risk_result['attack_type'],
                'risk_score': risk_result['risk_score'],
                'reason': block_reason,
                'action': 'BLOCKED'
            }), 403

        # Return None to allow request to proceed to route handler
        return None

    @app.after_request
    def log_api_response(response):
        # Exclude static assets and internal dashboard polling routes
        if request.path.startswith('/static') or request.path.startswith('/api/security'):
            return response


        latency = round((time.time() - getattr(g, 'start_time', time.time())) * 1000, 2)
        sec_ctx = getattr(g, 'security_context', {'risk_score': 0, 'action': 'ALLOW'})

        client_ip = getattr(g, 'client_ip', get_client_ip())

        # If a failed login attempt occurred, update risk context & check for Brute Force threshold
        status_code = response.status_code
        if request.path == '/api/login' and status_code == 401:
            stats = get_recent_request_stats(client_ip, window_seconds=60)
            if stats['failed_logins'] >= 4:
                sec_ctx['risk_score'] = 85
                sec_ctx['risk_level'] = 'CRITICAL'
                sec_ctx['action'] = 'BLOCKED'
                sec_ctx['attack_type'] = 'Brute Force Attack'
                sec_ctx['reason'] = f"High density of failed login attempts ({stats['failed_logins']} failures) from IP"
                block_ip_address(client_ip, reason=sec_ctx['reason'], duration_minutes=15)
            elif sec_ctx.get('risk_score', 0) < 40:
                sec_ctx['risk_score'] = 45
                sec_ctx['risk_level'] = 'MEDIUM'
                sec_ctx['action'] = 'MONITOR'
                sec_ctx['attack_type'] = 'Brute Force Suspicion'
                sec_ctx['reason'] = f"Multiple failed login attempts ({stats['failed_logins']} failures)"


        # Record API traffic log
        log_entry = ApiLog(
            timestamp=datetime.now(),
            ip_address=client_ip,
            method=request.method,
            endpoint=request.path,
            status_code=status_code,
            response_time_ms=latency,
            risk_score=sec_ctx.get('risk_score', 0),
            action_taken=sec_ctx.get('action', 'ALLOW')
        )
        db.session.add(log_entry)

        # Record security event if suspicious or elevated risk
        if sec_ctx.get('risk_score', 0) >= 35 or sec_ctx.get('attack_type', 'None') != 'None':
            sec_event = SecurityEvent(
                timestamp=datetime.now(),
                ip_address=client_ip,
                endpoint=request.path,
                attack_type=sec_ctx.get('attack_type', 'Suspicious Traffic'),
                risk_score=sec_ctx.get('risk_score', 35),
                risk_level=sec_ctx.get('risk_level', 'MEDIUM'),
                detection_method=sec_ctx.get('detection_method', 'RULE_ENGINE'),
                reason=sec_ctx.get('reason', 'Elevated risk score'),
                action_taken=sec_ctx.get('action', 'MONITOR')
            )
            db.session.add(sec_event)

        db.session.commit()
        return response
