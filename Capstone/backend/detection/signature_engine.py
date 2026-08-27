import json
from datetime import datetime, timedelta
from detection.rules import check_sqli, check_xss, check_path_traversal

def analyze_signature(request_obj, recent_failed_logins=0, recent_ip_requests=0):
    """
    Analyzes an incoming Flask request object against predefined signatures.
    Returns: dict { 'score': int, 'attack_types': list, 'reasons': list }
    """
    total_score = 0
    attack_types = []
    reasons = []

    # 1. Inspect URL Path & Query Parameters
    full_path = request_obj.full_path or request_obj.path or ''
    
    # Path Traversal Check
    has_pt, pt_reason = check_path_traversal(full_path)
    if has_pt:
        total_score += 65
        attack_types.append("Path Traversal / Recon Scanner")
        reasons.append(pt_reason)

    # SQL Injection in Query String
    has_sqli, sqli_reason = check_sqli(full_path)
    if has_sqli:
        total_score += 75
        attack_types.append("SQL Injection")
        reasons.append(sqli_reason)

    # XSS in Query String
    has_xss, xss_reason = check_xss(full_path)
    if has_xss:
        total_score += 70
        attack_types.append("Cross-Site Scripting (XSS)")
        reasons.append(xss_reason)

    # 2. Inspect Request Body (JSON or Form)
    body_str = ""
    try:
        if request_obj.is_json and request_obj.json:
            body_str = json.dumps(request_obj.json)
        elif request_obj.form:
            body_str = json.dumps(dict(request_obj.form))
        elif request_obj.data:
            body_str = request_obj.data.decode('utf-8', errors='ignore')
    except Exception:
        body_str = ""

    if body_str:
        has_body_sqli, body_sqli_reason = check_sqli(body_str)
        if has_body_sqli and "SQL Injection" not in attack_types:
            total_score += 75
            attack_types.append("SQL Injection")
            reasons.append(f"Body Payload: {body_sqli_reason}")

        has_body_xss, body_xss_reason = check_xss(body_str)
        if has_body_xss and "Cross-Site Scripting (XSS)" not in attack_types:
            total_score += 70
            attack_types.append("Cross-Site Scripting (XSS)")
            reasons.append(f"Body Payload: {body_xss_reason}")

    # 3. Failed Login / Brute Force Signature
    if recent_failed_logins >= 4:
        total_score += 80
        attack_types.append("Brute Force Attack")
        reasons.append(f"High density of failed login attempts ({recent_failed_logins} failures) from IP")
    elif recent_failed_logins >= 2:
        total_score += 40
        attack_types.append("Brute Force Suspicion")
        reasons.append(f"Multiple failed login attempts ({recent_failed_logins} failures)")


    # 4. Excessive Rate Limit Signature
    if recent_ip_requests > 25:
        total_score += 65
        attack_types.append("Rate Limit Violation")
        reasons.append(f"Burst request count of {recent_ip_requests} in 60s window exceeded threshold")

    return {
        'score': min(100, total_score),
        'attack_types': attack_types,
        'reasons': reasons
    }
