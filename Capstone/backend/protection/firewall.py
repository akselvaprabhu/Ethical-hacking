from datetime import datetime, timedelta
from database import db
from models.blocked_ip import BlockedIp
from models.alert import Alert

def check_ip_blocked(ip_address):
    """
    Checks if an IP address is currently blocked in the database.
    Returns: (is_blocked: bool, block_entry: BlockedIp | None)
    """
    block_entry = BlockedIp.query.filter_by(ip_address=ip_address, is_active=True).first()
    if not block_entry:
        return False, None

    if block_entry.expires_at and datetime.utcnow() > block_entry.expires_at:
        block_entry.is_active = False
        db.session.commit()
        return False, None

    return True, block_entry

def block_ip_address(ip_address, reason, duration_minutes=15):
    """
    Adds an IP address to the active blocked list and creates a security alert.
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=duration_minutes)

    existing = BlockedIp.query.filter_by(ip_address=ip_address, is_active=True).first()
    if existing:
        existing.reason = reason
        existing.expires_at = expires_at
        existing.blocked_at = now
    else:
        new_block = BlockedIp(
            ip_address=ip_address,
            reason=reason,
            blocked_at=now,
            expires_at=expires_at,
            is_active=True
        )
        db.session.add(new_block)

    # Create security alert
    alert = Alert(
        timestamp=now,
        severity='CRITICAL',
        title=f"IP Blocked: {ip_address}",
        message=f"IP {ip_address} automatically blocked for {duration_minutes}m. Reason: {reason}"
    )
    db.session.add(alert)
    db.session.commit()
    print(f"FIREWALL: Blocked IP {ip_address} until {expires_at}. Reason: {reason}")
    return True

def unblock_ip_address(ip_address):
    """
    Deactivates IP block entry in database.
    """
    blocks = BlockedIp.query.filter_by(ip_address=ip_address, is_active=True).all()
    if not blocks:
        return False
    for b in blocks:
        b.is_active = False
    db.session.commit()
    print(f"FIREWALL: Unblocked IP {ip_address}")
    return True
