import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models.user import User

def generate_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    secret_key = current_app.config['SECRET_KEY']
    return jwt.encode(payload, secret_key, algorithm='HS256')

def decode_token(token):
    try:
        secret_key = current_app.config['SECRET_KEY']
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'success': False, 'message': 'Authentication token missing', 'reason': 'Missing JWT token'}), 401
            
        decoded = decode_token(token)
        if 'error' in decoded:
            return jsonify({'success': False, 'message': 'Authentication failed', 'reason': decoded['error']}), 401
            
        current_user = User.query.get(decoded['user_id'])
        if not current_user:
            return jsonify({'success': False, 'message': 'User not found', 'reason': 'User record invalid'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'success': False, 'message': 'Authentication token missing', 'reason': 'Admin access requires JWT token'}), 401
            
        decoded = decode_token(token)
        if 'error' in decoded:
            return jsonify({'success': False, 'message': 'Authentication failed', 'reason': decoded['error']}), 401
            
        if decoded.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Forbidden', 'reason': 'Admin privileges required'}), 403
            
        current_user = User.query.get(decoded['user_id'])
        return f(current_user, *args, **kwargs)
    return decorated
