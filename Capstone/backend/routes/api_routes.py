from flask import Blueprint, request, jsonify
from utils.jwt_helper import token_required

api_bp = Blueprint('api', __name__)

SAMPLE_PRODUCTS = [
    {'id': 101, 'name': 'Cybersecurity Firewall Appliance', 'category': 'Hardware', 'price': 1299.99, 'stock': 15},
    {'id': 102, 'name': 'Intelligent Threat Detection Suite', 'category': 'Software', 'price': 499.99, 'stock': 100},
    {'id': 103, 'name': 'API Gateway Security Shield', 'category': 'Cloud', 'price': 799.00, 'stock': 50},
    {'id': 104, 'name': 'Zero-Trust Authentication Engine', 'category': 'Security', 'price': 299.50, 'stock': 80}
]

SAMPLE_ORDERS = [
    {'order_id': 'ORD-8821', 'product': 'Intelligent Threat Detection Suite', 'status': 'Delivered', 'amount': 499.99, 'date': '2026-08-22'},
    {'order_id': 'ORD-8822', 'product': 'API Gateway Security Shield', 'status': 'Processing', 'amount': 799.00, 'date': '2026-08-23'}
]

@api_bp.route('/api/products', methods=['GET'])
def get_products():
    search = request.args.get('search', '')
    if search:
        filtered = [p for p in SAMPLE_PRODUCTS if search.lower() in p['name'].lower()]
        return jsonify({'success': True, 'count': len(filtered), 'data': filtered}), 200
    return jsonify({'success': True, 'count': len(SAMPLE_PRODUCTS), 'data': SAMPLE_PRODUCTS}), 200

@api_bp.route('/api/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    return jsonify({
        'success': True,
        'user': current_user.username,
        'orders': SAMPLE_ORDERS
    }), 200

@api_bp.route('/api/orders', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    new_order = {
        'order_id': f'ORD-{request.id if hasattr(request, "id") else 9900 + len(SAMPLE_ORDERS)}',
        'user': current_user.username,
        'product_id': product_id,
        'quantity': quantity,
        'status': 'Confirmed',
        'date': '2026-08-23'
    }
    return jsonify({'success': True, 'message': 'Order created successfully', 'order': new_order}), 201

@api_bp.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'success': True,
        'profile': current_user.to_dict(),
        'security_status': 'Active JWT Session'
    }), 200
