def calculate_risk_score(signature_results, ml_anomaly_score, failed_login_count, request_freq):
    """
    Calculates dynamic risk score between 0 and 100.
    
    signature_results: dict with 'score', 'attack_types', 'reasons'
    ml_anomaly_score: float (0.0 to 1.0, higher means more anomalous)
    failed_login_count: int count of recent failed logins
    request_freq: int requests in last 60s window
    """
    base_score = 0
    reasons = []
    attack_types = []
    
    # 1. Signature Rule Score Contribution
    sig_score = signature_results.get('score', 0)
    base_score += sig_score
    if signature_results.get('reasons'):
        reasons.extend(signature_results['reasons'])
    if signature_results.get('attack_types'):
        attack_types.extend(signature_results['attack_types'])
        
    # 2. ML Anomaly Score Contribution (Scale 0-1 to 0-40 points)
    if ml_anomaly_score > 0.3:
        ml_points = int(ml_anomaly_score * 40)
        base_score += ml_points
        attack_types.append("Behavioral Anomaly (ML)")
        reasons.append(f"ML Isolation Forest detected statistical anomaly (score: {ml_anomaly_score:.2f})")
        
    # 3. Failed Login Boost
    if failed_login_count >= 3:
        failed_boost = min(30, failed_login_count * 8)
        base_score += failed_boost
        if "Brute Force" not in attack_types:
            attack_types.append("Brute Force Warning")
            reasons.append(f"{failed_login_count} recent failed login attempts detected")
            
    # 4. Excessive Frequency Boost
    if request_freq > 15:
        freq_boost = min(25, (request_freq - 15) * 3)
        base_score += freq_boost
        if "Rate Limit Violation" not in attack_types:
            attack_types.append("Excessive Request Burst")
            reasons.append(f"High traffic frequency ({request_freq} req/min)")
            
    # Clamp final score between 0 and 100
    final_score = min(100, max(0, base_score))
    
    # Classify Risk Level
    if final_score <= 30:
        risk_level = 'LOW'
        action = 'ALLOW'
    elif final_score <= 60:
        risk_level = 'MEDIUM'
        action = 'MONITOR'
    elif final_score <= 80:
        risk_level = 'HIGH'
        action = 'RATE_LIMIT'
    else:
        risk_level = 'CRITICAL'
        action = 'BLOCK'
        
    # Override action if explicit critical signature matched (e.g. SQLi / Hard Brute Force)
    if sig_score >= 70:
        action = 'BLOCK'
        if final_score < 75:
            final_score = 85
            risk_level = 'CRITICAL'
            
    return {
        'risk_score': final_score,
        'risk_level': risk_level,
        'action': action,
        'attack_type': ', '.join(set(attack_types)) if attack_types else 'None',
        'reason': '; '.join(reasons) if reasons else 'Normal API behavior'
    }
