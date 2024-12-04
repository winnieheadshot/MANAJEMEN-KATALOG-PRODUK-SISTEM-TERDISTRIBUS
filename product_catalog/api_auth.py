# api_auth.py
from functools import wraps
from flask import request, jsonify
import secrets

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is missing'}), 401
            
        # Check API key in database
        conn = None
        try:
            conn = db.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM api_keys WHERE key_value = %s AND is_active = 1', (api_key,))
            key_data = cursor.fetchone()
            
            if not key_data:
                return jsonify({'error': 'Invalid API key'}), 401
                
            return f(*args, **kwargs)
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    return decorated_function